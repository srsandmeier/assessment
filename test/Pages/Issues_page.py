from playwright.sync_api import Page, expect

class IssuesPage:
    def __init__(self, page: Page):
        # Store the Playwright page instance so all methods can access it
        self.page = page

        self.outer_frame = self.page.frame_locator("#outerFrame")
        self.inner_frame = self.outer_frame.frame_locator("#appFrame")
        self.cards_locator = self.inner_frame.locator(".issue-card")
        self.confirm_bar = self.inner_frame.locator("#confirmBar")
        self.selected_count_span = self.inner_frame.locator("#selectedCount")

    


    def record_final_value_before_change(self, card_index: int):
        #Extracts the original row value and asserts that the final row matches it.
        card = self.cards_locator.nth(card_index)
        
        # Locators on this card
        final_span = card.locator("tr[data-row-type='final'] div.cell-editable span")

        current_value = final_span.text_content().strip()
        print(f"Current Final Value for card {card_index + 1}: {current_value}")
        return current_value


    def select_original_value_for_card(self, card_index: int):
       #Clicks the original radio button for a given card index.
        card = self.cards_locator.nth(card_index)
        original_row = card.locator("tr[data-row-type='original']")
        
        original_row.get_by_role("radio", name="Select original value:").click()

    def verify_final_value_matches_original(self, card_index: int):
        #Extracts the original row value and asserts that the final row matches it.
        card = self.cards_locator.nth(card_index)
        
        # Locators on this card
        original_span = card.locator("tr[data-row-type='original'] td.cell-issue span")
        final_span = card.locator("tr[data-row-type='final'] div.cell-editable span")
        
        # Extract the expected text from the original row
        expected_text = original_span.text_content().strip()
        
        # Assert the final matches the text
        expect(final_span).to_have_text(expected_text)

        updated_text = final_span.text_content().strip()
        print(f"Changed Final Value for card {card_index + 1}: {updated_text}")
        return updated_text

    def get_card_by_sfid(self, sfid: str):
       
        #Finds and returns the specific card by SFID
        # Target the specific cell inside the original row containing the SFID
        target_sfid_cell = "tr[data-row-type='original'] td:last-child span"
        
        # Filter down all cards to find the one matching the text
        return self.cards_locator.filter(has=self.inner_frame.locator(target_sfid_cell), has_text=sfid)

    def edit_street_field_by_sfid(self, sfid: str, new_value: str = "123 Test Street"):
        #Locates the street field, reads/prints the old value, clears it, updates it, and verifies.
        card = self.get_card_by_sfid(sfid)
        
        editable_address = card.locator("tr[data-row-type='final'] div[data-field='Street']")
        text_span = editable_address.locator("span")
       
        old_value = text_span.text_content().strip()
        print(f"\n[INFO] Current Street Value: {old_value}")

        editable_address.click()
        input_field = editable_address.locator("input, textarea").first
            
        input_field.fill("")         # Clear field
        input_field.fill(new_value)  # Type new text
        
        input_field.press("Enter")
       
        expect(text_span).to_have_text(new_value)
        
        final_value = text_span.text_content().strip()
        print(f"[INFO] New Street Value: {final_value}")
        
        return final_value


    def select_cards_by_numbers(self, card_numbers: list[int]):
       #Loops through a list of human-input card numbers (where Number = Index + 1) converts them to indexes, and selects them.
      
        print(f"\n[INFO] Starting selection loop for cards: {card_numbers}")
        
        for number in card_numbers:
            # Convert to index
            index = number - 1
           
            card = self.cards_locator.nth(index)
            checkbox = card.locator("input.issue-checkbox")
            
            checkbox.check()
            print(f" -> Successfully selected Card #{number} (at index {index})")

    def verify_confirm_bar_count(self, expected_count: int):
        if expected_count > 0:
            expect(self.confirm_bar).to_have_class("confirm-bar visible")
            expect(self.selected_count_span).to_have_text(str(expected_count))
            print(f"[SUCCESS] Confirm bar visible with correct count: {expected_count}")
        else:
            expect(self.confirm_bar).to_have_class("confirm-bar")

            expect(self.selected_count_span).to_have_text("0")
            print("[SUCCESS] Confirm bar hidden and count reset to 0.")

    def unselect_cards_by_numbers(self, card_numbers: list[int]):
        #Loops through list and unchecks them.
    
        print(f"\n[INFO] Unselecting cards: {card_numbers}")
        for number in card_numbers:
            # Convert
            index = number - 1
            
            # uncheck it
            checkbox = self.cards_locator.nth(index).locator("input.issue-checkbox")
            checkbox.uncheck()
            print(f" -> Unselected Card #{number} (at index {index})")