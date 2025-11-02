"""
Name:      r.watershed accumulation tests
Purpose:   Validates the flow accumulation calculation

Author:    Māris Nartišs
Copyright: (C) 2025 by Māris Nartišs and the GRASS Development Team
Licence:   This program is free software under the GNU General Public
           License (>=v2). Read the file COPYING that comes with GRASS
           for details.
"""

from grass.script import read_command
from grass.gunittest.case import TestCase
from grass.gunittest.main import test


class WatershedAccumulationTest(TestCase):
    """Test r.watershed accumulation calculation"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        cls.use_temp_region()
        cls.runModule("g.region", n=10, s=0, e=10, w=0, res=1)
        cls.runModule(
            "r.mapcalc",
            expression="dem_row = row()",
            overwrite=True,
        )

    @classmethod
    def tearDownClass(cls):
        """Remove temporary data"""
        cls.del_temp_region()
        cls.runModule(
            "g.remove",
            flags="f",
            type="raster",
            name=("dem_row", "acc_row_test"),
        )

    def test_accumulation_abs_noedge_ram(self):
        """Test accumulation ignoring edge impact with -a flag in RAM mode"""
        self.runModule(
            "r.watershed",
            flags="sae",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number. The last row is 10.
        expected_first_row = "10 10 10 10 10 10 10 10 10 10"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_abs_noedge_seg(self):
        """Test accumulation ignoring edge impact with -a flag in SEG mode"""
        self.runModule(
            "r.watershed",
            flags="saem",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number. The last row is 10.
        expected_first_row = "10 10 10 10 10 10 10 10 10 10"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_abs_edge_ram(self):
        """Test accumulation not counting edges in with -a flag in RAM mode"""
        self.runModule(
            "r.watershed",
            flags="sa",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number -1 for edge.
        expected_first_row = "1 9 9 9 9 9 9 9 9 1"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_abs_edge_seg(self):
        """Test accumulation not counting edges in with -a flag in SEG mode"""
        self.runModule(
            "r.watershed",
            flags="sam",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number - 1 for edge.
        expected_first_row = "1 9 9 9 9 9 9 9 9 1"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_noedge_ram(self):
        """Test accumulation ignoring edge impact in RAM mode"""
        self.runModule(
            "r.watershed",
            flags="se",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number. The last row is 10.
        expected_first_row = "-10 -10 -10 -10 -10 -10 -10 -10 -10 -10"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_noedge_seg(self):
        """Test accumulation ignoring edge impact in SEG mode"""
        self.runModule(
            "r.watershed",
            flags="sem",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number. The last row is 10.
        expected_first_row = "-10 -10 -10 -10 -10 -10 -10 -10 -10 -10"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_edge_ram(self):
        """Test accumulation not counting edges in RAM mode"""
        self.runModule(
            "r.watershed",
            flags="s",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number - 1 for edge.
        expected_first_row = "-1 -9 -9 -9 -9 -9 -9 -9 -9 -1"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )

    def test_accumulation_edge_seg(self):
        """Test accumulation not counting edges in SEG mode"""
        self.runModule(
            "r.watershed",
            flags="sm",
            elevation="dem_row",
            accumulation="acc_row_test",
            overwrite=True,
            quiet=True,
        )

        # For a simple `dem = row()`, accumulation in each cell of a given
        # row should be equal to the inverse row number - 1 for edge.
        expected_first_row = "-1 -9 -9 -9 -9 -9 -9 -9 -9 -1"

        output = read_command("r.out.ascii", flags="h", input="acc_row_test").strip()
        rows = output.split("\n")
        first_row = rows[0].strip()
        self.assertEqual(
            first_row,
            expected_first_row,
            f"First row is incorrect. Expected: '{expected_first_row}', but got '{first_row}'",
        )


if __name__ == "__main__":
    test()
