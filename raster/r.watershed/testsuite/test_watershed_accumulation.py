from grass.gunittest.case import TestCase
from grass.gunittest.main import test


class TestWatershedAccumulationSFD(TestCase):
    """
    Tests r.watershed flow accumulation of single flow direction
    """

    to_remove = []

    @classmethod
    def setUpClass(cls):
        cls.use_temp_region()
        cls.runModule("g.region", n=10, s=0, e=10, w=0, res=1)
        cls.runModule("r.mapcalc", expression="elevation = 10 - row()", overwrite=True)
        cls.to_remove.append("elevation")

    @classmethod
    def tearDownClass(cls):
        cls.del_temp_region()
        if cls.to_remove:
            cls.runModule(
                "g.remove", flags="f", type="raster", name=",".join(cls.to_remove)
            )

    def test_flow_required(self):
        """Accumulation min and max make sense only if flow is provided"""

        self.assertModuleFail(
            "r.watershed",
            elevation="elevation",
            accum_min="accumulation_min",
            overwrite=True,
            msg="Flow is required",
        )
        self.assertModuleFail(
            "r.watershed",
            elevation="elevation",
            accum_max="accumulation_max",
            overwrite=True,
            msg="Flow is required",
        )

    def test_accumulation_on_slope(self):
        """Test default accumulation"""

        self.to_remove.extend(
            [
                "accumulation_seg",
                "accumulation_ram",
                "expected_accumulation",
            ]
        )

        # Use negatives to indicate edge impact
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_ram",
            flags="s",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_seg",
            flags="sm",
            overwrite=True,
            quiet=True,
        )

        # Output in both modes should be identical
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )

        self.runModule(
            "r.mapcalc",
            expression=(
                "expected_accumulation = if(col() == 1 || col() == 10 "
                "|| row() == 1, -1, -row() + 1)"
            ),
            overwrite=True,
        )
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="expected_accumulation",
            precision=0,
        )

        # Ignore edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_ram",
            flags="sa",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_seg",
            flags="sam",
            overwrite=True,
            quiet=True,
        )

        # Output in both modes should be identical
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )

        self.runModule(
            "r.mapcalc",
            expression=(
                "expected_accumulation = if(col() == 1 || col() == 10 "
                "|| row() == 1, 1, row() - 1)"
            ),
            overwrite=True,
        )
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="expected_accumulation",
            precision=0,
        )

    def test_flow_ones_on_slope(self):
        """Test accumulation of a flow (all ones)"""

        self.to_remove.extend(
            [
                "accumulation_ram",
                "accum_min_ones_ram",
                "accum_max_ones_ram",
                "accumulation_seg",
                "accum_min_ones_seg",
                "accum_max_ones_seg",
                "accumulation_seg_abs",
                "accumulation_ram_abs",
                "expected_accum_minmax",
                "flow_ones",
            ]
        )

        self.runModule("r.mapcalc", expression="flow_ones = 1", overwrite=True)

        # With edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_ram",
            accum_min="accum_min_ones_ram",
            accum_max="accum_max_ones_ram",
            flags="s",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_seg",
            accum_min="accum_min_ones_seg",
            accum_max="accum_max_ones_seg",
            flags="sm",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="accum_min_ones_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="accum_max_ones_seg",
            precision=0,
        )

        self.runModule(
            "r.mapcalc", expression=("expected_accum_minmax = 1"), overwrite=True
        )

        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )

        # Without edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_ram",
            accum_min="accum_min_ones_ram",
            accum_max="accum_max_ones_ram",
            flags="sa",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_seg",
            accum_min="accum_min_ones_seg",
            accum_max="accum_max_ones_seg",
            flags="sam",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="accum_min_ones_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="accum_max_ones_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )

    def test_accum_col_on_slope(self):
        """Test accumulation of a flow (column number)"""

        self.to_remove.extend(
            [
                "accumulation_ram",
                "accumulation_seg",
                "accum_min_col_ram",
                "accum_max_col_ram",
                "accum_min_col_seg",
                "accum_max_col_seg",
                "expected_accumulation",
                "expected_accum_minmax",
                "flow_col",
            ]
        )

        self.runModule("r.mapcalc", expression="flow_col = col()", overwrite=True)

        # With edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_ram",
            accum_min="accum_min_col_ram",
            accum_max="accum_max_col_ram",
            flags="s",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_seg",
            accum_min="accum_min_col_seg",
            accum_max="accum_max_col_seg",
            flags="sm",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="accum_max_col_seg",
            precision=0,
        )

        self.runModule(
            "r.mapcalc",
            expression=(
                "expected_accumulation = if(col() == 1, -1, "
                "if(col() == 10, -10, "
                "if(row() == 1, -col(), (-row() + 1) * col())))"
            ),
            overwrite=True,
        )
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="expected_accumulation",
            precision=0,
        )

        self.runModule(
            "r.mapcalc",
            expression=(
                "expected_accum_minmax = if(col() == 1, 1, if(col() == 10, 10, col()))"
            ),
            overwrite=True,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="expected_accum_minmax",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="expected_accum_minmax",
            precision=0,
        )

        # Without edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_ram",
            accum_min="accum_min_col_ram",
            accum_max="accum_max_col_ram",
            flags="sa",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_seg",
            accum_min="accum_min_col_seg",
            accum_max="accum_max_col_seg",
            flags="sam",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="accum_max_col_seg",
            precision=0,
        )

        self.runModule(
            "r.mapcalc",
            expression=(
                "expected_accumulation = if(col() == 1, 1, "
                "if(col() == 10, 10, "
                "if(row() == 1, col(), (row() - 1) * col())))"
            ),
            overwrite=True,
        )
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="expected_accumulation",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="expected_accum_minmax",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="expected_accum_minmax",
            precision=0,
        )


class TestWatershedAccumulationMFD(TestCase):
    """
    Tests r.watershed accumulation and contribution accumulation
    """

    to_remove = []

    @classmethod
    def setUpClass(cls):
        cls.use_temp_region()
        cls.runModule("g.region", n=10, s=0, e=10, w=0, res=1)
        cls.runModule("r.mapcalc", expression="elevation = 10 - row()", overwrite=True)
        cls.to_remove.append("elevation")

    @classmethod
    def tearDownClass(cls):
        cls.del_temp_region()
        if cls.to_remove:
            cls.runModule(
                "g.remove", flags="f", type="raster", name=",".join(cls.to_remove)
            )

    def test_accumulation_on_slope(self):
        """Test accumulation on a slope with MFD"""

        self.to_remove.extend(
            [
                "accumulation_ram",
                "accumulation_seg",
            ]
        )

        # Use negatives to indicate edge impact
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_ram",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_seg",
            flags="m",
            overwrite=True,
            quiet=True,
        )

        # As MFD implementation is not fully deterministic, it is hard
        # to implement one "gold standard" thus just check if two modes
        # give identical results. Not an ideal situation.

        # Output in both modes should be identical
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )

        # Ignore edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_ram",
            flags="a",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            accumulation="accumulation_seg",
            flags="am",
            overwrite=True,
            quiet=True,
        )

        # Output in both modes should be identical
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )

    def test_accum_ones_on_slope(self):
        """Test accumulation of a flow (all ones)"""

        self.to_remove.extend(
            [
                "accumulation_ram",
                "accumulation_ram",
                "accum_min_ones_ram",
                "accum_max_ones_ram",
                "accumulation_seg",
                "accumulation_seg",
                "accum_min_ones_seg",
                "accum_max_ones_seg",
                "accumulation_ram_abs",
                "expected_accum_minmax",
                "flow_ones",
            ]
        )

        # Flow to accumulate – just a constant for testing
        self.runModule("r.mapcalc", expression="flow_ones = 1", overwrite=True)

        # Reference map
        self.runModule(
            "r.mapcalc", expression=("expected_accum_minmax = 1"), overwrite=True
        )

        # With edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_ram",
            accum_min="accum_min_ones_ram",
            accum_max="accum_max_ones_ram",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_seg",
            accum_min="accum_min_ones_seg",
            accum_max="accum_max_ones_seg",
            flags="m",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="accum_min_ones_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="accum_max_ones_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )

        # Without edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_ram",
            accum_min="accum_min_ones_ram",
            accum_max="accum_max_ones_ram",
            flags="a",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ones",
            accumulation="accumulation_seg",
            accum_min="accum_min_ones_seg",
            accum_max="accum_max_ones_seg",
            flags="am",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="accum_min_ones_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="accum_max_ones_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_ones_ram",
            reference="expected_accum_minmax",
            precision=0,
        )

    def test_accum_col_on_slope_lr(self):
        """Test accumulation of flow (column number)"""

        self.to_remove.extend(
            [
                "expected_accum_max",
                "expected_accum_min",
                "accumulation_ram",
                "accum_min_col_ram",
                "accum_max_col_ram",
                "accumulation_seg",
                "accum_min_col_seg",
                "accum_max_col_seg",
                "flow_col",
            ]
        )

        # Reference maps
        max_ascii = """north: 10
south: 0
east: 10
west: 0
rows: 10
cols: 10
1 2 3 4 5 6 7 8 9 10
1 2 3 4 5 6 7 8 9 10
2 3 4 5 6 7 8 9 9 10
3 4 5 6 7 8 9 9 9 10
4 5 6 7 8 9 9 9 9 10
5 6 7 8 9 9 9 9 9 10
6 7 8 9 9 9 9 9 9 10
7 8 9 9 9 9 9 9 9 10
8 9 9 9 9 9 9 9 9 10
9 9 9 9 9 9 9 9 9 10
"""
        min_ascii = """north: 10
south: 0
east: 10
west: 0
rows: 10
cols: 10
1 2 3 4 5 6 7 8 9 10
1 2 3 4 5 6 7 8 9 10
1 2 2 3 4 5 6 7 8 9
1 2 2 2 3 4 5 6 7 8
1 2 2 2 2 3 4 5 6 7
1 2 2 2 2 2 3 4 5 6
1 2 2 2 2 2 2 3 4 5
1 2 2 2 2 2 2 2 3 4
1 2 2 2 2 2 2 2 2 3
1 2 2 2 2 2 2 2 2 2
"""
        self.assertModule(
            "r.in.ascii",
            input="-",
            output="expected_accum_max",
            type="CELL",
            stdin_=max_ascii,
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.in.ascii",
            input="-",
            output="expected_accum_min",
            type="CELL",
            stdin_=min_ascii,
            overwrite=True,
            quiet=True,
        )

        # Flow to accumulate 1...10
        self.runModule("r.mapcalc", expression="flow_col = col()", overwrite=True)

        # With edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_ram",
            accum_min="accum_min_col_ram",
            accum_max="accum_max_col_ram",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_seg",
            accum_min="accum_min_col_seg",
            accum_max="accum_max_col_seg",
            flags="m",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="accum_max_col_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="expected_accum_min",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="expected_accum_max",
            precision=0,
        )

        # Without edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_ram",
            accum_min="accum_min_col_ram",
            accum_max="accum_max_col_ram",
            flags="a",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_col",
            accumulation="accumulation_seg",
            accum_min="accum_min_col_seg",
            accum_max="accum_max_col_seg",
            flags="am",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="accum_max_col_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="expected_accum_min",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="expected_accum_max",
            precision=0,
        )

    def test_accum_col_on_slope_rl(self):
        """Test accumulation of flow (reverse column number)"""

        self.to_remove.extend(
            [
                "expected_accum_max",
                "expected_accum_min",
                "accumulation_ram",
                "accum_min_col_ram",
                "accum_max_col_ram",
                "accumulation_seg",
                "accum_min_col_seg",
                "accum_max_col_seg",
                "flow_ncol",
            ]
        )

        # Reference data
        max_ascii = """north: 10
south: 0
east: 10
west: 0
rows: 10
cols: 10
10 9 8 7 6 5 4 3 2 1
10 9 8 7 6 5 4 3 2 1
10 9 9 8 7 6 5 4 3 2
10 9 9 9 8 7 6 5 4 3
10 9 9 9 9 8 7 6 5 4
10 9 9 9 9 9 8 7 6 5
10 9 9 9 9 9 9 8 7 6
10 9 9 9 9 9 9 9 8 7
10 9 9 9 9 9 9 9 9 8
10 9 9 9 9 9 9 9 9 9
"""
        min_ascii = """north: 10
south: 0
east: 10
west: 0
rows: 10
cols: 10
10 9 8 7 6 5 4 3 2 1
10 9 8 7 6 5 4 3 2 1
9 8 7 6 5 4 3 2 2 1
8 7 6 5 4 3 2 2 2 1
7 6 5 4 3 2 2 2 2 1
6 5 4 3 2 2 2 2 2 1
5 4 3 2 2 2 2 2 2 1
4 3 2 2 2 2 2 2 2 1
3 2 2 2 2 2 2 2 2 1
2 2 2 2 2 2 2 2 2 1
"""
        self.assertModule(
            "r.in.ascii",
            input="-",
            output="expected_accum_max",
            type="CELL",
            stdin_=max_ascii,
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.in.ascii",
            input="-",
            output="expected_accum_min",
            type="CELL",
            stdin_=min_ascii,
            overwrite=True,
            quiet=True,
        )

        # Flow to accumulate: 10...1
        self.runModule("r.mapcalc", expression="flow_ncol = 11 - col()", overwrite=True)

        # With edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ncol",
            accumulation="accumulation_ram",
            accum_min="accum_min_col_ram",
            accum_max="accum_max_col_ram",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ncol",
            accumulation="accumulation_seg",
            accum_min="accum_min_col_seg",
            accum_max="accum_max_col_seg",
            flags="m",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="expected_accum_min",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="expected_accum_max",
            precision=0,
        )

        # Without edge effect
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ncol",
            accumulation="accumulation_ram",
            accum_min="accum_min_col_ram",
            accum_max="accum_max_col_ram",
            flags="a",
            overwrite=True,
            quiet=True,
        )
        self.assertModule(
            "r.watershed",
            elevation="elevation",
            flow="flow_ncol",
            accumulation="accumulation_seg",
            accum_min="accum_min_col_seg",
            accum_max="accum_max_col_seg",
            flags="am",
            overwrite=True,
            quiet=True,
        )

        # RAM and SEG mode should produce identical results
        self.assertRastersNoDifference(
            actual="accumulation_ram",
            reference="accumulation_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="accum_min_col_seg",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="accum_max_col_seg",
            precision=0,
        )

        self.assertRastersNoDifference(
            actual="accum_min_col_ram",
            reference="expected_accum_min",
            precision=0,
        )
        self.assertRastersNoDifference(
            actual="accum_max_col_ram",
            reference="expected_accum_max",
            precision=0,
        )


if __name__ == "__main__":
    test()
