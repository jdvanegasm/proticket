Feature: Create Event Post
  As an organizer
  I want to create an event post
  So that it can be listed for sale

  Scenario: Successful event creation
    Given the backend is running
    And an existing organizer with credentials
    When I create a new event with valid data
    Then I should receive a 200 status code
    And the response should contain the event information
