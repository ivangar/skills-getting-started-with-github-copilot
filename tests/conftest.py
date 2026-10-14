import pytest


@pytest.fixture
def test_data():
    return {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" and not (report.when == "setup" and report.failed):
        return

    result = report.outcome.upper()
    tested_data = item.funcargs.get("test_data", {})
    terminal_reporter = item.config.pluginmanager.get_plugin("terminalreporter")
    if terminal_reporter is not None:
        terminal_reporter.write_line(
            f"{result}: {item.nodeid} | assertion result: {result.lower()} | "
            f"data tested: {tested_data!r}"
        )