/*
 * r.smooth
 *
 *   Copyright 2024 by Maris Nartiss, and The GRASS Development Team
 *   Author: Maris Nartiss
 *
 *   This program is free software licensed under the GPL (>=v2).
 *   Read the COPYING file that comes with GRASS for details.
 *
 */

#include <grass/gis.h>
#include <grass/rowio.h>

struct Row_cache {
    ROWIO rowio_cache;
    bool use_rowio;
    int tmp_fd;
    char *tmp_name;
    /* nrows are of cache and not computational region */
    int nrows;
    int ncols;
    size_t len;
    DCELL **matrix;
    void (*fill)(DCELL *, int, struct Row_cache *);
    DCELL *(*get)(int, struct Row_cache *);
    void (*put)(DCELL *, int, struct Row_cache *);
};

struct PM_params {
    const char *in_map;
    const char *in_mapset;
    const char *out_map;
    double vert_cor, diag_cor;
    /* nrows are of computational region */
    int nrows, ncols;
    int conditional;
    int steps;
    double contrast2;
    double scale;
    double dt;
};

/* row_cache.c */
int rowio_get_row(int fd, void *buffer, int row, int buffer_length);
int rowio_put_row(int fd, const void *buffer, int row, int buffer_length);
DCELL *get_rowio(int row, struct Row_cache *row_cache);
void put_rowio(DCELL *buf, int row, struct Row_cache *row_cache);
DCELL *get_ram(int row, struct Row_cache *row_cache);
void put_ram(DCELL *buf, int row, struct Row_cache *row_cache);
void setup_row_cache(int nrows, int ncols, double max_ram,
                     struct Row_cache *row_cache);
void teardown_row_cache(struct Row_cache *row_cache);
void fill_ram(DCELL *buf, int row, struct Row_cache *row_cache);
void fill_rowio(DCELL *buf, int row, struct Row_cache *row_cache);

/* pm.c */
void pm(const struct PM_params *pm_params, struct Row_cache *row_cache);
