#include <grass/gis.h>
#include <unistd.h>
#include <fcntl.h>
#include <grass/glocale.h>
#include "Gwater.h"

int cseg_open(CSEG *cseg, int srows, int scols, int nsegs_in_memory)
{
    char *filename;
    int errflag;
    int ret = 0;

    cseg->filename = NULL;
    cseg->fd = -1;
    cseg->name = NULL;
    cseg->mapset = NULL;

    filename = G_tempfile();
    if (0 > (errflag = Segment_open(&(cseg->seg), filename, Rast_window_rows(),
                                    Rast_window_cols(), srows, scols,
                                    sizeof(CELL), nsegs_in_memory))) {
        if (errflag == -1) {
            G_warning(_("File name is invalid"));
            ret = -1;
        }
        else if (errflag == -2) {
            G_warning(_("File write error"));
            ret = -2;
        }
        else if (errflag == -3) {
            G_warning(_("Illegal parameters are passed"));
            ret = -3;
        }
        else if (errflag == -4) {
            G_warning(_("File could not be re-opened"));
            ret = -4;
        }
        else if (errflag == -5) {
            G_warning(_("Prepared file could not be read"));
            ret = -5;
        }
        else if (errflag == -6) {
            G_warning(_("Out of memory"));
            ret = -6;
        }
        G_free(filename);
        return ret;
    }

    cseg->filename = filename;

    return ret;
}
