from flask import Flask, request, jsonify, abort
import logging
from src.schedule_manager import ScheduleManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/generate-schedule', methods=['POST'])
def generate_schedule():
    data = request.json
    if not data:
        abort(400, "Request body is missing or not in JSON format")
    
    try:
        if 'middle_school' not in data and 'high_school' not in data:
            abort(400, "At least one of 'middle_school' or 'high_school' must be provided")
        
        rooms = data.get('rooms', [])
        teachers = data.get('teachers', [])
        
        if not rooms:
            abort(400, "Rooms data is missing or empty")
        if not teachers:
            abort(400, "Teachers data is missing or empty")

        schedule_manager = ScheduleManager(data, rooms, teachers)
        schedules = schedule_manager.generate_schedules()

        logger.info("Successfully generated schedules")

        return jsonify(schedules), 200
    
    
    except KeyError as e:
        logger.error(f"Key error during schedule generation: {str(e)}")
        return jsonify({"error": f"Missing key in request data: {str(e)}"}), 400
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during schedule generation: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
