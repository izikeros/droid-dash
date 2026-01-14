Feature: Dashboard Navigation
  As a user
  I want to navigate between dashboard tabs
  So that I can view different analytics views

  Background:
    Given the dashboard is running with test data

  Scenario: Navigate to Overview tab
    When I press "1" to switch tabs
    Then I should see the Overview tab content

  Scenario: Navigate to Groups tab
    When I press "2" to switch tabs
    Then I should see the Groups tab content
    And I should see share bar charts

  Scenario: Navigate to Projects tab
    When I press "3" to switch tabs
    Then I should see the Projects tab content
    And I should see a sortable projects table

  Scenario: Navigate to Sessions tab
    When I press "4" to switch tabs
    Then I should see the Sessions tab content
    And I should see session controls for sorting and grouping

  Scenario: Navigate to Favorites tab
    When I press "5" to switch tabs
    Then I should see the Favorites tab content

  Scenario: Navigate to Settings tab
    When I press "6" to switch tabs
    Then I should see the Settings tab content
    And I should see configuration options
