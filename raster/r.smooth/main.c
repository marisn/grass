/****************************************************************************
 *
 * MODULE:       r.smooth
 * AUTHOR(S):    Maris Nartiss maris.gis gmail.com
 * PURPOSE:      Provides smoothing with anisotropic diffusion according to:
 *               Perona P. and Malik J. 1990. Scale-space and edge detection
 *               using anisotropic diffusion. IEEE transactions on pattern
 *               analysis and machine intelligence, 12(7).
 *               Tukey's conductance function according to:
 *               Black M.J., Sapiro G., Marimont D.H. and Heeger D. 1998.
 *               Robust anisotropic diffusion. IEEE transactions on image
 *               processing, 7(3).
 *
 * COPYRIGHT:    (C) 2024 by Maris Nartiss and the GRASS Development Team
 *
 *               This program is free software under the GNU General Public
 *   	    	 License (>=v2). Read the file COPYING that comes with GRASS
 *   	    	 for details.
 *
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <float.h>
#include <math.h>
#if defined(_OPENMP)
#include <omp.h>
#endif

#include <grass/gis.h>
#include <grass/rowio.h>
#include <grass/raster.h>
#include <grass/manage.h>
#include <grass/glocale.h>
#include "local_proto.h"

int main(int argc, char *argv[])
{
    struct GModule *module;

    struct {
        struct Option *input, *output, *K, *l, *t, *met, *mem;
        struct Flag *old;
    } opt;

    G_gisinit(argv[0]);

    /* initialize module */
    module = G_define_module();
    G_add_keyword(_("raster"));
    G_add_keyword(_("smoothing"));
    G_add_keyword(_("edge detection"));
    module->description = _("Smoothing with anisotropic diffusion");

    opt.input = G_define_standard_option(G_OPT_R_INPUT);

    opt.output = G_define_standard_option(G_OPT_R_OUTPUT);

    opt.K = G_define_option();
    opt.K->key = "threshold";
    opt.K->type = TYPE_DOUBLE;
    opt.K->required = YES;
    opt.K->description = _("Gradient magnitude threshold (in map units)");
    opt.K->guisection = _("Diffusion");
    opt.K->answer = "5";
    opt.K->options = "0.000000001-";

    opt.l = G_define_option();
    opt.l->key = "lambda";
    opt.l->type = TYPE_DOUBLE;
    opt.l->required = YES;
    opt.l->description = _("Rate of diffusion (0,1]");
    opt.l->guisection = _("Diffusion");
    opt.l->answer = "0.1";
    opt.l->options = "0-1";

    opt.t = G_define_option();
    opt.t->key = "steps";
    opt.t->type = TYPE_INTEGER;
    opt.t->required = YES;
    opt.t->description = _("Number of diffusion steps");
    opt.t->guisection = _("Diffusion");
    opt.t->answer = "10";
    opt.t->options = "1-";

    opt.met = G_define_option();
    opt.met->key = "conditional";
    opt.met->type = TYPE_STRING;
    opt.met->required = YES;
    opt.met->description = _("Conductance function");
    opt.met->options = "exponental,quadratic,tukey";
    opt.met->answer = "tukey";

    opt.mem = G_define_standard_option(G_OPT_MEMORYMB);

    /* Temporary development option */
    opt.old = G_define_flag();
    opt.old->key = 'o';
    opt.old->label = "Use old code";

    if (G_parser(argc, argv))
        exit(EXIT_FAILURE);

    struct PM_params pm_params;
    const char *in_map, *out_map, *in_mapset;
    in_map = opt.input->answer;
    out_map = opt.output->answer;
    /* K and lambda could be determined from the data. See formula #21
     * and following discussion in the Black et al. 1998
     */
    double threshold = atof(opt.K->answer);
    double lambda = atof(opt.l->answer);
    pm_params.steps = atoi(opt.t->answer);

    pm_params.contrast2 = threshold * threshold;
    pm_params.scale = threshold * sqrt(2);

    /* Silence compiler warnings */
    pm_params.conditional = 3;
    pm_params.dt = 1;

    if (strncmp(opt.met->answer, "tuk", 3) == 0) {
        pm_params.conditional = 3;
        pm_params.dt = lambda;
    }
    else if (strncmp(opt.met->answer, "exp", 3) == 0) {
        pm_params.conditional = 1;
        /* Equations are stable only if 0<= lambda <= 0.25
         * according to Perona P. and Malik J. 1990 */
        pm_params.dt = lambda > 0.25 ? 0.25 : lambda;
    }
    else if (strncmp(opt.met->answer, "qua", 3) == 0) {
        pm_params.conditional = 2;
        pm_params.dt = lambda > 0.25 ? 0.25 : lambda;
    }
    /* Lambda needs to be devided by number of neighbours
     * according to formula 5 in Black et al. 1998 */
    pm_params.dt = pm_params.dt / 8.0;

    in_mapset = (char *)G_find_raster2(in_map, "");
    if (in_mapset == NULL)
        G_fatal_error(_("Raster map <%s> not found"), in_map);

    struct Cell_head window;
    Rast_get_window(&window);
    if (window.ew_res < GRASS_EPSILON) {
        G_fatal_error(_("Wrong computational region"));
    }
    pm_params.nrows = window.rows;
    pm_params.ncols = window.cols;
    if (pm_params.nrows < 3 || pm_params.ncols < 3) {
        G_fatal_error(_("Computational region is too small!"));
    }

    /* Static adjustment for non-square cells.
     * Should be replaced with much more expensice true per-row distance
     * calculation for a ll location. */
    pm_params.vert_cor = window.ns_res / window.ew_res;
    pm_params.diag_cor =
        sqrt(window.ns_res * window.ns_res + window.ew_res * window.ew_res) /
        window.ew_res;
    pm_params.in_map = in_map;
    pm_params.in_mapset = in_mapset;
    pm_params.out_map = out_map;

    struct Row_cache row_cache;
    setup_row_cache(pm_params.nrows, pm_params.ncols, atof(opt.mem->answer),
                    &row_cache);
    pm(&pm_params, &row_cache);
    teardown_row_cache(&row_cache);

    struct Colors colors;
    const char *out_mapset = G_mapset();
    if (Rast_read_colors(in_map, in_mapset, &colors) < 0) {
        Rast_init_colors(&colors);
        if (Rast_map_type(in_map, in_mapset) == CELL_TYPE) {
            struct Range range;
            CELL min, max;
            Rast_read_range(out_map, out_mapset, &range);
            Rast_get_range_min_max(&range, &min, &max);
            Rast_make_grey_scale_colors(&colors, min, max);
            Rast_write_colors(out_map, out_mapset, &colors);
        }
        else {
            struct FPRange range;
            DCELL min, max;
            Rast_read_fp_range(in_map, in_mapset, &range);
            Rast_get_fp_range_min_max(&range, &min, &max);
            Rast_make_grey_scale_fp_colors(&colors, min, max);
            Rast_write_colors(out_map, out_mapset, &colors);
        }
        Rast_free_colors(&colors);
    }
    else {
        Rast_write_colors(out_map, out_mapset, &colors);
        Rast_free_colors(&colors);
    }

    struct History history;
    Rast_put_cell_title(out_map, _("Smoothed map"));
    Rast_short_history(out_map, "raster", &history);
    Rast_set_history(&history, HIST_DATSRC_1, in_map);
    Rast_command_history(&history);
    Rast_write_history(out_map, &history);

    exit(EXIT_SUCCESS);
}
