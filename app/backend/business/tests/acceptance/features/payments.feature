Feature: Online Checkout Payment
  As a buyer
  I want to complete a payment online
  So that I can confirm my ticket purchase

  Scenario: Successful online payment
    And an existing order
    When I create a new payment with valid data
    Then I should receive a 201 status code
    And the payment status should be "pending"

  Scenario: Updating a payment to completed
    Given an existing payment
    When I update the payment status to "completed"
    Then the payment status should be "completed"
