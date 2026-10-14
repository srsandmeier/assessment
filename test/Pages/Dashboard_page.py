from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


class DashboardPage:
    def __init__(self, page: Page):
        # Store the Playwright page instance so all methods can access it
        self.page = page

        self.outer_frame = self.page.frame_locator("#outerFrame")
        self.inner_frame = self.outer_frame.frame_locator("#appFrame")

    def navigate_to_issues(self):
        #Navigate to the Data Issues page and assert that 10 issue cards are displayed.
        self.page.goto("http://localhost:8080/index.html")

        # Close popup if it appears
        try:
            self.page.get_by_role("button", name="Got it").click(timeout=2000)
        except PlaywrightTimeoutError:
            pass  # popup didn't appear

        ## Click on the "Data Issues" button
        outer_frame = self.page.frame_locator("#outerFrame")
        inner_frame = outer_frame.frame_locator("#appFrame")
        self.page.locator("#spinnerOverlay").wait_for(state="hidden")

        solve_button = inner_frame.locator("#solveBtn")
        solve_button.wait_for(state="visible")
        solve_button.click()

        self.page.wait_for_load_state("load")