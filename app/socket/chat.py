from flask_socketio import emit, join_room


def register_socket(socketio):

    @socketio.on("join")
    def join(data):
        join_room(data["room"])

    @socketio.on("message")
    def message(data):
        emit("message", data["message"], to=data["room"])
