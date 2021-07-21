$(document).ready(function() {
    const poll_interval = 333;

    let rest_path = window.location.pathname.split('/').slice(0, -2).join('/') + "/rest";

    function makeid() {
        var result = "";
        var characters =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        var charactersLength = characters.length;
        for (var i = 0; i < 20; i++) {
            result += characters.charAt(
                Math.floor(Math.random() * charactersLength)
            );
        }

        return result;
    }

    var client_id = makeid();

    var chatWindow = new Bubbles(
        document.getElementById("chat"),
        "chatWindow",
        {
            inputCallbackFn: function (chatObject) {
                input = chatObject.input;

                $.post(rest_path + "/chat/" + client_id, input);
            },
        }
    );

    var poll = function () {
        $.get(rest_path + "/chat/" + client_id)
            .done(function (data) {
                chatWindow.talk({
                        talk: {
                            says: data,
                            reply: [],
                        },
                    },
                    "talk"
                );
            })
            .always(function(){setTimeout(poll, poll_interval)});
    }

    var convo = {
        ice: {
            says: ["Hi"],
        },
    };

    chatWindow.talk(convo);
    poll();
});