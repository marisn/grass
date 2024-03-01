/*
 * r.smooth Perona & Malik smoothing
 *
 *   Copyright 2024 by Maris Nartiss, and The GRASS Development Team
 *   Author: Maris Nartiss
 *
 *   This program is free software licensed under the GPL (>=v2).
 *   Read the COPYING file that comes with GRASS for details.
 *
 */
#include <string.h>
#include <math.h>

#include <grass/gis.h>
#include <grass/raster.h>

#include "local_proto.h"

void pm(const struct PM_params *pm_params, struct Row_cache *row_cache)
{
    /* Copy initial data to the tmp file */
    int in_fd = Rast_open_old(pm_params->in_map, pm_params->in_mapset);
    RASTER_MAP_TYPE data_type =
        Rast_map_type(pm_params->in_map, pm_params->in_mapset);

    /* Sliding rows (above, current, below + modified) */
    DCELL *out = G_malloc((pm_params->ncols + 2) * sizeof(DCELL));
    DCELL *ra = G_malloc((pm_params->ncols + 2) * sizeof(DCELL));
    DCELL *rc;
    DCELL *rb;
    /* We'll use nrows + 2 pad rows at each end + 2 pad cols */
    Rast_get_d_row(in_fd, &out[1], 0);
    out[0] = out[1];
    out[pm_params->ncols + 1] = out[pm_params->ncols];
    row_cache->fill(out, 0, row_cache);
    for (unsigned int row = 0; row < pm_params->nrows; row++) {
        Rast_get_d_row(in_fd, &out[1], row);
        out[0] = out[1];
        out[pm_params->ncols + 1] = out[pm_params->ncols];
        row_cache->fill(out, row + 1, row_cache);
    }
    row_cache->fill(out, pm_params->nrows + 1, row_cache);
    Rast_close(in_fd);

    /* No padding for gradients and divs */
    DCELL **gradients, **divs, *di;
    di = (DCELL *)G_malloc(pm_params->ncols * sizeof(DCELL));
    gradients = (DCELL **)G_malloc(8 * sizeof(DCELL *));
    divs = (DCELL **)G_malloc(8 * sizeof(DCELL *));
#pragma GCC unroll 8
    for (unsigned int i = 0; i < 8; i++) {
        gradients[i] = (DCELL *)G_malloc(pm_params->ncols * sizeof(DCELL));
        divs[i] = (DCELL *)G_malloc(pm_params->ncols * sizeof(DCELL));
    }

    /* A single step */
    for (int step = 0; step < pm_params->steps; step++) {
        /* Prefill rows */
        rc = row_cache->get(0, row_cache);
        rb = row_cache->get(1, row_cache);
        row_cache->put(out, 0, row_cache);

        /* Loop over padded data */
        for (unsigned int prow = 1; prow < pm_params->nrows + 1; prow++) {
            /* Slide down by a single row */
            out = ra;
            ra = rc;
            rc = rb;
            rb = row_cache->get(prow + 1, row_cache);

#pragma omp parallel for
            for (unsigned int pcol = 1; pcol <= pm_params->ncols; pcol++) {
                gradients[0][pcol - 1] =
                    (ra[pcol] - rc[pcol]) * pm_params->vert_cor;
                gradients[1][pcol - 1] =
                    (rb[pcol] - rc[pcol]) * pm_params->vert_cor;
                gradients[2][pcol - 1] =
                    (ra[pcol - 1] - rc[pcol]) * pm_params->diag_cor;
                gradients[3][pcol - 1] =
                    (ra[pcol + 1] - rc[pcol]) * pm_params->diag_cor;
                gradients[4][pcol - 1] = rc[pcol + 1] - rc[pcol];
                gradients[5][pcol - 1] = rc[pcol - 1] - rc[pcol];
                gradients[6][pcol - 1] =
                    (rb[pcol - 1] - rc[pcol]) * pm_params->diag_cor;
                gradients[7][pcol - 1] =
                    (rb[pcol + 1] - rc[pcol]) * pm_params->diag_cor;

                /* Use 0 for nan gradients to not propogate holes */
                gradients[0][pcol - 1] =
                    gradients[0][pcol - 1] != gradients[0][pcol - 1]
                        ? 0
                        : gradients[0][pcol - 1];
                gradients[1][pcol - 1] =
                    gradients[1][pcol - 1] != gradients[1][pcol - 1]
                        ? 0
                        : gradients[1][pcol - 1];
                gradients[2][pcol - 1] =
                    gradients[2][pcol - 1] != gradients[2][pcol - 1]
                        ? 0
                        : gradients[2][pcol - 1];
                gradients[3][pcol - 1] =
                    gradients[3][pcol - 1] != gradients[3][pcol - 1]
                        ? 0
                        : gradients[3][pcol - 1];
                gradients[4][pcol - 1] =
                    gradients[4][pcol - 1] != gradients[4][pcol - 1]
                        ? 0
                        : gradients[4][pcol - 1];
                gradients[5][pcol - 1] =
                    gradients[5][pcol - 1] != gradients[5][pcol - 1]
                        ? 0
                        : gradients[5][pcol - 1];
                gradients[6][pcol - 1] =
                    gradients[6][pcol - 1] != gradients[6][pcol - 1]
                        ? 0
                        : gradients[6][pcol - 1];
                gradients[7][pcol - 1] =
                    gradients[7][pcol - 1] != gradients[7][pcol - 1]
                        ? 0
                        : gradients[7][pcol - 1];
            }

            /* Calculate conductance coefficient */
            if (pm_params->conditional == 3) {
                /* Black et al. 1998 Tukey's biweight function */
#pragma omp parallel for
                for (unsigned int col = 0; col < pm_params->ncols; col++) {
                    if (pm_params->scale < fabs(gradients[0][col]) ||
                        pm_params->scale < fabs(gradients[1][col]) ||
                        pm_params->scale < fabs(gradients[2][col]) ||
                        pm_params->scale < fabs(gradients[3][col]) ||
                        pm_params->scale < fabs(gradients[4][col]) ||
                        pm_params->scale < fabs(gradients[5][col]) ||
                        pm_params->scale < fabs(gradients[6][col]) ||
                        pm_params->scale < fabs(gradients[7][col])) {
                        gradients[0][col] = 0;
                        gradients[1][col] = 0;
                        gradients[2][col] = 0;
                        gradients[3][col] = 0;
                        gradients[4][col] = 0;
                        gradients[5][col] = 0;
                        gradients[6][col] = 0;
                        gradients[7][col] = 0;
                    }
#pragma GCC unroll 8
                    for (unsigned int i = 0; i < 8; i++) {
                        divs[i][col] =
                            gradients[i][col] * 0.5 *
                            ((1 - ((gradients[i][col] * gradients[i][col]) /
                                   (pm_params->scale * pm_params->scale))) *
                             (1 - ((gradients[i][col] * gradients[i][col]) /
                                   (pm_params->scale * pm_params->scale))));
                    }
                }
            }
            else if (pm_params->conditional == 1) {
/* Perona & Malik 1st conductance function = exponential */
#pragma omp parallel for
                for (unsigned int col = 0; col < pm_params->ncols; col++) {
#pragma GCC unroll 8
                    for (unsigned int i = 1; i < 8; i++) {
                        divs[i][col] =
                            gradients[i][col] *
                            exp(-1.0 *
                                ((gradients[i][col] * gradients[i][col]) /
                                 pm_params->contrast2));
                    }
                }
            }
            else if (pm_params->conditional == 2) {
/* Perona & Malik 2nd conductance function = quadratic */
#pragma omp parallel for
                for (unsigned int col = 0; col < pm_params->ncols; col++) {
#pragma GCC unroll 8
                    for (unsigned int i = 1; i < 8; i++) {
                        divs[i][col] =
                            gradients[i][col] * 1 /
                            (1 + ((gradients[i][col] * gradients[i][col]) /
                                  pm_params->contrast2));
                    }
                }
            }

/* Calculate new values and add padding */
#pragma omp parallel for
            for (unsigned int col = 0; col < pm_params->ncols; col++) {
                di[col] = divs[0][col] + divs[1][col] + divs[2][col] +
                          divs[3][col] + divs[4][col] + divs[5][col] +
                          divs[6][col] + divs[7][col];
                out[col + 1] = di[col] * pm_params->dt + rc[col + 1];
            }
            out[0] = out[1];
            out[pm_params->ncols + 1] = out[pm_params->ncols];

            /* Write out values to tmp file
             * out can not be reused as it might point to a row in row_cache
             */
            row_cache->put(out, prow, row_cache);
        }
        out = ra;
        ra = rc;
        /* Clone new values to padding rows */
        DCELL *tmp;
        tmp = row_cache->get(0, row_cache);
        memcpy(tmp, row_cache->get(1, row_cache), row_cache->len);
        row_cache->put(tmp, 0, row_cache);
        tmp = row_cache->get(pm_params->nrows + 1, row_cache);
        memcpy(tmp, row_cache->get(pm_params->nrows, row_cache),
               row_cache->len);
        row_cache->put(tmp, pm_params->nrows + 1, row_cache);
    } // step
    /* Let out and ra leak, as they might be freed by caching functions */
    G_free(di);

#pragma GCC ivdep
    for (unsigned int i = 0; i < 8; i++) {
        G_free(gradients[i]);
        G_free(divs[i]);
    }
    G_free(gradients);
    G_free(divs);

    /* Write out final data */
    int out_fd = Rast_open_new(pm_params->out_map, data_type);
    switch (data_type) {
    case DCELL_TYPE:
        for (unsigned int row = 0; row < pm_params->nrows; row++) {
            double *dbuf = row_cache->get(row + 1, row_cache);
            Rast_put_d_row(out_fd, &(dbuf[1]));
        }
        break;
    case FCELL_TYPE:
        FCELL *fbuf = (FCELL *)G_malloc(pm_params->ncols * sizeof(FCELL));
        for (unsigned int row = 0; row < pm_params->nrows; row++) {
            double const *dbuf = row_cache->get(row + 1, row_cache);
/* Get rid of padding and cast to output type */
#pragma GCC ivdep
            for (unsigned int col = 0; col < pm_params->ncols; col++) {
                fbuf[col] = (FCELL)dbuf[col + 1];
            }
            Rast_put_f_row(out_fd, fbuf);
        }
        G_free(fbuf);
        break;
    case CELL_TYPE:
        CELL *cbuf = G_malloc(pm_params->ncols * sizeof(CELL));
        for (unsigned int row = 0; row < pm_params->nrows; row++) {
            double const *dbuf = row_cache->get(row + 1, row_cache);
/* Get rid of padding and cast to output type */
#pragma GCC ivdep
            for (unsigned int col = 0; col < pm_params->ncols; col++) {
                cbuf[col] = (CELL)round(dbuf[col + 1]);
            }
            Rast_put_c_row(out_fd, cbuf);
        }
        G_free(cbuf);
        break;
    }

    Rast_close(out_fd);
}
