from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_login_bu_selection_and_home_start_without_exception():
    app = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    assert not at.exception
    at.text_input[0].set_value("viewer")
    at.text_input[1].set_value("ChangeMe!2026")
    at.button[0].click().run()
    assert not at.exception
    at.selectbox[0].set_value("Cement")
    at.button[0].click().run()
    assert not at.exception
    labels = [button.label.split("\n", 1)[0] for button in at.button]
    assert {"Readings", "Open Flags", "Events", "Lessons", "Notifications"}.issubset(labels)
