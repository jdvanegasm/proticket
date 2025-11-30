Feature: View event statistics
  As an organizer
  I want to see sales and remaining capacity
  So that I can track performance

  Scenario: Organizer retrieves event statistics successfully
    Given the backend is running
    And an existing event with sales
    When I fetch the statistics for the organizer
    Then I should receive a 200 status code
    And the response should include the event statistics
