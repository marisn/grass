#include <stdio.h>
#include <grass/gis.h>
#include <grass/raster.h>

void check_ready(void);
int adjcellhd(struct Cell_head *cellhd);
void rdwr_gridatb(void);


extern struct Cell_head cellhd;
extern FCELL *cell;
extern const char *file;
extern const char *iname;
extern char overwr;
