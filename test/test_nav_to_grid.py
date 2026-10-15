import re
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError
import test
from Pages.Dashboard_page import DashboardPage
from Pages.Issues_page import IssuesPage

def test_has_grid(page: Page):
    dashboard_page = DashboardPage(page)
    page.goto("http://localhost:8080/index.html")

    print(f"\n[INFO] Starting {test_has_grid.__name__}: test to validate the Data Issues grid and issue cards.")
    ### Test 1: Navigate to the Data Issues grid
    #Navigate to the Data Issues page and assert that 10 issue cards are displayed.

    # Close popup if it appears
    try:
        page.get_by_role("button", name="Got it").click(timeout=2000)
    except PlaywrightTimeoutError:
        pass  # popup didn't appear

    # Validate that the page has loaded by checking for the presence of the logo
    ##expect(page.locator("span.logo")).to_have_text("GenericCRM")
    expect(dashboard_page.inner_frame.locator("#breadcrumb-current")).to_have_text("Dashboard")

    ## Click on the "Data Issues" button
    outer_frame = page.frame_locator("#outerFrame")
    inner_frame = outer_frame.frame_locator("#appFrame")
    page.locator("#spinnerOverlay").wait_for(state="hidden")

    solve_button = inner_frame.locator("#solveBtn")
    solve_button.wait_for(state="visible")
    solve_button.click()

    # Wait for the page to load and validate correct page is seen and has the grid
    page.wait_for_load_state("load")
    expect(inner_frame.locator("#breadcrumb-current")).to_have_text("Data Issues")
    expect(inner_frame.locator("[class='issue-card']").first).to_be_visible()

    #Validate that 10 issue cards are displayed 
    #(*Note only some of these have a data-testid so used class)
    #(Ideally expected would not be hardcoded but come from a compare of the incoming JSON or in this case Mock_data against some filter)
    # and would also compare the value in <span class="badge" aria-label="10 issues">10</span> 
    # There would also be a test to validate the data sent in the API matches the DB
    expected = 10
    expect(inner_frame.locator("[class='issue-card']")).to_have_count(expected)
    print(f"[INFO] Expected number of issue cards: {expected} Actual: {inner_frame.locator('[class=\"issue-card\"]').count()}")
    print("---------------------------------------------------\n")

def test_cards_have_sfid(page: Page):
    dashboard_page = DashboardPage(page)
    issues_page = IssuesPage(page)

    ### Test 2: Extract and validate all issue data
    #From the Data Issues grid, extract the original row data from all 10 issue cards. Assert that each card's original row contains a non-empty sfid value.

    dashboard_page.navigate_to_issues()

    expect(issues_page.inner_frame.locator("#breadcrumb-current")).to_have_text("Data Issues")
    expect(issues_page.cards_locator.first).to_be_visible()
    expect(issues_page.cards_locator).to_have_count(10)

    # Get the original row data from all 10 issue cards

    cards_list = issues_page.cards_locator.all()
    print(f"\n[INFO] Starting test {test_cards_have_sfid.__name__}: to extract and validate SFID values from all issue cards.")
    print(f"[INFO] Extracting SFID Values for {len(cards_list)} Cards ---")

    #Loop through each card
    for card in cards_list:
        index = cards_list.index(card)
        original_sfid_locator = card.locator("tr[data-row-type='original'] td:last-child span")
    
        expect(original_sfid_locator).to_be_visible()
        
        sfid_text = original_sfid_locator.text_content().strip()
        
        print(f"[INFO] Card #{index + 1}: Verified Original SFID: {sfid_text}")
        assert sfid_text != "" and sfid_text != "—", f"Card #{index + 1} has an invalid sfid: '{sfid_text}'"
    print("---------------------------------------------------\n")

def test_update_issue_value_radio(page: Page):
    dashboard_page = DashboardPage(page)
    issues_page = IssuesPage(page)
    print(f"\n[INFO] Starting test {test_update_issue_value_radio.__name__}: to update issue value using radio button selection.")
    ### Test 3: Select a specific issue and change its value
    #Locate the 7th issue card on the grid. Select the **original** value for the issue column. Assert that the final row updated to reflect the original value.

    dashboard_page.navigate_to_issues()

    expect(issues_page.inner_frame.locator("#breadcrumb-current")).to_have_text("Data Issues")
    expect(issues_page.inner_frame.locator("[class='issue-card']").first).to_be_visible()

    # Locate the 7th issue card specifically (index 6)
    seventh_card = issues_page.cards_locator.nth(6)
    
    # Verify the 7th card is visible
    expect(seventh_card).to_be_visible()
    
    phone_header = seventh_card.locator("th", has=page.locator("span", has_text="Phone"))
    expect(phone_header).to_be_visible()

    # Verify it is the correct card by checking the originalvalue
    original_sfid_locator = seventh_card.locator("tr[data-row-type='original'] td:last-child span")
    if original_sfid_locator.count() > 0:
        sfid_value = original_sfid_locator.text_content().strip()
        print(f"\n[INFO] 7th Card SFID: {sfid_value}")

    column_name = "Phone"
    issues_page.record_final_value_before_change(6, column=column_name)
    issues_page.select_original_value_for_card(6, column=column_name)
    issues_page.verify_final_value_matches_original(6, column=column_name)
    print("---------------------------------------------------\n")

def test_update_issue_value_text(page: Page):
    dashboard_page = DashboardPage(page)
    issues_page = IssuesPage(page)
    print(f"\n[INFO] Starting test {test_update_issue_value_text.__name__}:to update issue value using text input.") 

    ### Test 4: Edit a final row field
    #Locate the issue card with sfid `00Qak00000RHtuzEAD`. 
    #Edit the issue column in the final row — 
    #clear the existing value, 
    #type `123 Test Street`, and 
    #confirm the edit. Assert the final row displays `123 Test Street`.

    dashboard_page.navigate_to_issues()

    expect(issues_page.inner_frame.locator("#breadcrumb-current")).to_have_text("Data Issues")
    expect(issues_page.inner_frame.locator("[class='issue-card']").first).to_be_visible()

    target_sfid = "00Qak00000RHtuzEAD" 

    issues_page.edit_street_field_by_sfid(target_sfid, "123 Test Street")

    print("---------------------------------------------------\n")

def test_select_issues_multiple(page: Page):
    dashboard_page = DashboardPage(page)
    issues_page = IssuesPage(page)
    print(f"\n[INFO] Starting test {test_select_issues_multiple.__name__}: to select multiple issues.")
    ### Test 5: Checkbox selection count
    #select the checkboxes on the 1st, 3rd, and 5th issue cards. 
    #Assert the selection counter shows `3 issue(s) selected`. 
    #Select all issues and assert the counter shows `10 issue(s) selected`. 
    #Deselect all and assert the counter is no longer visible.

    dashboard_page.navigate_to_issues()

    expect(issues_page.inner_frame.locator("#breadcrumb-current")).to_have_text("Data Issues")
    expect(issues_page.inner_frame.locator("[class='issue-card']").first).to_be_visible()


    cards_to_select = [1, 3, 5]
    more_cards_to_select = [2, 4, 6, 7, 8, 9, 10]
    cards_to_unselect = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    issues_page.verify_confirm_bar_count(expected_count=0)

    issues_page.select_cards_by_numbers(cards_to_select)
    
    issues_page.verify_confirm_bar_count(expected_count=len(cards_to_select))

    issues_page.select_cards_by_numbers(more_cards_to_select)

    issues_page.verify_confirm_bar_count(expected_count=10)
    issues_page.verify_confirm_bar_count(expected_count=len(cards_to_select) + len(more_cards_to_select))

    issues_page.unselect_cards_by_numbers(cards_to_unselect)

    issues_page.verify_confirm_bar_count(expected_count=0)