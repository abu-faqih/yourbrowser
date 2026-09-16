"""
Unit tests for YourBrowser Design System tokens & style helpers.
"""

import unittest
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary, pill_badge, rounded_input
)
from src.resources.style import BRAVE_THEME_QSS


class TestDesignSystem(unittest.TestCase):

    def test_colors_tokens_exist(self):
        self.assertTrue(Colors.BG_CANVAS.startswith("#"))
        self.assertTrue(Colors.ACCENT_ORANGE.startswith("#"))
        self.assertTrue(Colors.ACCENT_CYAN.startswith("#"))
        self.assertTrue(Colors.STATUS_SUCCESS.startswith("#"))

    def test_gradients_tokens_valid(self):
        self.assertIn("qlineargradient", Gradients.PRIMARY_FLAME)
        self.assertIn("qlineargradient", Gradients.CYBER_CYAN)
        self.assertIn("qlineargradient", Gradients.SURFACE_CARD)

    def test_radii_tokens(self):
        self.assertEqual(Radii.XS, "4px")
        self.assertEqual(Radii.MD, "12px")
        self.assertEqual(Radii.LG, "16px")
        self.assertEqual(Radii.PILL, "9999px")

    def test_pill_button_primary_helper(self):
        qss = pill_button_primary(height=36)
        self.assertIn("border-radius: 18px", qss)
        self.assertIn(Gradients.PRIMARY_FLAME, qss)
        self.assertIn("QPushButton", qss)

    def test_pill_button_secondary_helper(self):
        qss = pill_button_secondary(height=40)
        self.assertIn("border-radius: 20px", qss)
        self.assertIn(Colors.SURFACE_2, qss)

    def test_pill_badge_helper(self):
        badge_qss = pill_badge(Colors.STATUS_SUCCESS_BG, Colors.STATUS_SUCCESS)
        self.assertIn(Radii.PILL, badge_qss)
        self.assertIn(Colors.STATUS_SUCCESS, badge_qss)

    def test_rounded_input_helper(self):
        input_qss = rounded_input(height=38, radius="10px")
        self.assertIn("border-radius: 10px", input_qss)
        self.assertIn(Colors.BG_BASE, input_qss)

    def test_brave_theme_qss_contains_design_system_elements(self):
        self.assertIn("border-radius: 19px", BRAVE_THEME_QSS)  # Omnibox capsule
        self.assertIn(Gradients.PRIMARY_FLAME, BRAVE_THEME_QSS)
        self.assertIn(Colors.BG_CANVAS, BRAVE_THEME_QSS)


if __name__ == "__main__":
    unittest.main()
