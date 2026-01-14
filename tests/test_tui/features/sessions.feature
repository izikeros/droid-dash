Feature: Sessions Tab
  As a user
  I want to browse and manage my Droid sessions
  So that I can analyze my AI coding usage

  Background:
    Given the dashboard is running with test data
    And I am on the Sessions tab

  Scenario: View sessions list
    Then I should see a table with sessions
    And the sessions table should have data rows

  Scenario: Select a session to view prompts
    When I select the first session in the table
    Then the prompts panel should update
    And I should see session prompt information

  Scenario: Toggle favorite status
    When I select the first session in the table
    And I press "f" to toggle favorite
    Then the session favorite status should change

  Scenario: Sort sessions by different columns
    When I change the sort order to "date_desc"
    Then the sessions should be sorted by date descending

  Scenario: Group sessions by project
    When I change the grouping to "project"
    Then the sessions should be grouped by project

  Scenario: Hide empty sessions
    When the "hide empty sessions" filter is enabled
    Then I should not see sessions with zero prompts
