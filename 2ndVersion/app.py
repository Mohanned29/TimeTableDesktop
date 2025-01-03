from flask import Flask, request, jsonify, abort
from src.schedule_manager import ScheduleManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/generate-schedule', methods=['POST'])
def generate_schedule():
    data = request.json
    if not data:
        logger.error("No JSON payload received.")
        abort(400, description="Request body is missing or not in JSON format")

    try:
        if 'teachers' not in data or not data['teachers']:
            logger.error("Teachers data is missing or empty.")
            abort(400, description="Teachers data is missing or empty")
        if 'rooms' not in data or not data['rooms']:
            logger.error("Rooms data is missing or empty.")
            abort(400, description="Rooms data is missing or empty")
        if 'middle_school' not in data and 'high_school' not in data:
            logger.error("Neither middle_school nor high_school data provided.")
            abort(400, description="At least one of 'middle_school' or 'high_school' must be provided")

        schedule_manager = ScheduleManager(data)
        schedules = schedule_manager.generate_schedules()

        if not schedules:
            logger.error("Failed to generate schedules due to internal error.")
            abort(500, description="Failed to generate schedules due to internal error.")

        logger.info("Successfully generated schedules.")
        return jsonify(schedules), 200

    except KeyError as e:
        logger.error(f"Key error: {str(e)}")
        abort(400, description=f"Missing key in data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        abort(500, description=f"Internal server error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
