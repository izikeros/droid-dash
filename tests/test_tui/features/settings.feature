Feature: Settings Tab
  As a user
  I want to configure dashboard settings
  So that I can customize my experience

  Background:
    Given the dashboard is running with test data
    And I am on the Settings tab

  Scenario: View current configuration
    Then I should see display settings section
    And I should see column visibility options
    And I should see pricing configuration
    And I should see the config file path

  Scenario: Toggle dark mode setting
    When I toggle the dark mode checkbox
    Then the dark mode setting should change

  Scenario: Change default sort order
    When I select "date_desc" as the default sort
    Then the default sort setting should be "date_desc"
