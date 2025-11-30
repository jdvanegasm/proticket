Feature: List upcoming events
  As a buyer
  I want to see upcoming events
  So that I can choose one to buy tickets

  Scenario: Buyer retrieves the list of events successfully
    Given the system contains upcoming events
    When the buyer requests the list of events
    Then the response status should be 200
    And the response should contain a list of events
