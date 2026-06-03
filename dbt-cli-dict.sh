# dbt-cli-dict.sh
# A helpful dictionary of dbt CLI commands/flags and their descriptions.
# Reference this file for quick reminders about the dbt command line interface!

echo "DBT CLI COMMANDS & FLAGS DICTIONARY"
echo "==================================="

echo ""
echo "General Commands:"
echo "-----------------"
echo "dbt --version"
echo "    Shows the currently installed dbt version."

echo "dbt debug"
echo "    Tests your dbt configuration, connection, and environment setup."

echo "dbt init [project_name]"
echo "    Initializes a new dbt project in a subdirectory called [project_name]."

echo ""
echo "Build & Run Commands:"
echo "---------------------"
echo "dbt run"
echo "    Executes the dbt models (build tables/views defined in models/)."

echo "dbt build"
echo "    Runs models, tests, seeds, and snapshots as a full build pipeline."
echo "    (Shortcut for: dbt run + dbt test + dbt seed + dbt snapshot)"

echo "dbt test"
echo "    Runs tests on your data as defined in tests/ and inside model files."

echo "dbt seed"
echo "    Loads CSV seed files located in the seeds/ directory into your warehouse."

echo "dbt snapshot"
echo "    Executes snapshot logic to track changes in snapshot tables over time."

echo ""
echo "Source & Documentation Commands:"
echo "-------------------------------"
echo "dbt source freshness"
echo "    Checks the freshness of your source data (run on sources with freshness specified)."

echo "dbt docs generate"
echo "    Generates documentation for your dbt project."

echo "dbt docs serve"
echo "    Serves the documentation locally at http://localhost:8080."

echo ""
echo "Cleaning and Compilation:"
echo "------------------------"
echo "dbt clean"
echo "    Deletes compiled files and cleans up the dbt environment."

echo "dbt compile"
echo "    Compiles your dbt models without running them (renders SQL into target/)."

echo ""
echo "Flags & Options:"
echo "---------------"
echo "--profiles-dir [DIR]"
echo "    Override the directory where dbt looks for the profiles.yml file."

echo "--project-dir [DIR]"
echo "    Override the directory of the dbt project (default: current directory)."

echo "--select [model/table/tag]"
echo "-s [model/table/tag]"
echo "    Selects specific resources (models, sources, snapshots, tests, etc.) to run/compile/test."

echo "--exclude [model/table/tag]"
echo "-x [model/table/tag]"
echo "    Excludes specific resources from a run/compile/test."

echo "--full-refresh"
echo "    Drops incremental models and re-creates them from scratch."

echo "--target [target-name]"
echo "    Use a profile target other than the default."

echo "--vars '{\"var_name\": \"value\"}'"
echo "    Pass variables (as a JSON string) to your dbt project."

echo "--threads [N]"
echo "    Sets the number of threads dbt uses while running models."

echo ""
echo "dbt-codegen"
echo "---------------------"
echo "dbt run-operation generate_source --args '{"schema_name": "claims", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'"

echo ""
echo "More Info:"
echo "----------"
echo "See the dbt docs for more: https://docs.getdbt.com/reference/commands"