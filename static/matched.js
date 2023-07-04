const header = document.getElementById("header"),
  footer = document.getElementById("footer"),
  socket = io.connect(location.origin + "/");

var roomId;

function newMessageYou(id, time, msg) {
  return (
    '<li class="you">' +
    '<div class="entete">' +
    "<h2>" +
    document.querySelector('[id="' + id + '"] div div').innerHTML +
    "</h2>" +
    "<h3>" +
    time +
    "</h3>" +
    "</div>" +
    '<div class="triangle"></div>' +
    '<div class="message">' +
    msg +
    "</div>" +
    "</li>"
  );
}

function newMessageMe(time, msg) {
  return (
    '<li class="me">' +
    '<div class="entete">' +
    "<h2>Me</h2>" +
    "<h3>" +
    time +
    "</h3>" +
    "</div>" +
    '<div class="triangle"></div>' +
    '<div class="message">' +
    msg +
    "</div>" +
    "</li>"
  );
}

// Connects to socket.io chat and sets up event listener for incoming messages and then draws last messages from every chat
window.onload = function () {
  const lis = document.getElementById("aside").getElementsByTagName("li");
  for (let element of lis) {
    const room = getRoomIdFromUsersIds(element.id);
    socket.emit("create", room);
  }
  socket.on("message", function (data) {
    const [msg, room] = data;
    const miniChat = document
      .getElementById(decodeRoomIdToUsers(room))
      .getElementsByTagName("h3")[0];
    miniChat.innerHTML = "OTHER: " + shortMessage(msg);
    if (roomId === room) {
      chat.innerHTML += newMessageYou(
        decodeRoomIdToUsers(room),
        timeFormat(new Date()),
        msg
      );
      chat.scrollTop = chat.scrollHeight;
    }
  });
  socket.on("redirect", function (data) {
    const redirectData = data;
    if (redirectData.id === currentUser) {
      setTimeout(() => {
        window.location = redirectData.url;
      }, 1000);
    }
  });
};

// Shortens string message if is longer than 12 letters
function shortMessage(txt) {
  if (txt.length > 12) {
    return txt.slice(0, 9) + "...";
  } else {
    return txt;
  }
}

function showChat(id) {
  roomId = getRoomIdFromUsersIds(id);
  drawHeader(id);
  drawFooter(id);
  getChatHistory(id);
}

function drawHeader(id) {
  const img_src = document.querySelector('[id="' + id + '"] img').src,
    name = document.querySelector('[id="' + id + '"] div div').innerHTML;
  header.innerHTML =
    '<img src="' +
    img_src +
    '" alt=""/>' +
    '<div><h2 class="is-size-5">' +
    name +
    "</h2></div>";
}

function drawFooter() {
  footer.innerHTML =
    '<textarea id="text-area" placeholder="Type your message"></textarea>' +
    '<button id="send" onclick="send()" class="button is-primary">Send</button>';
}

// Sends new chat message
function send() {
  const textArea = document.getElementById("text-area");
  const msg = textArea.value;
  miniChat = document
    .getElementById(decodeRoomIdToUsers(String(roomId)))
    .getElementsByTagName("h3")[0];
  socket.emit("message", [msg, roomId]);
  miniChat.innerHTML = "ME: " + shortMessage(msg);
  chat.innerHTML += newMessageMe(timeFormat(new Date()), msg);
  chat.scrollTop = chat.scrollHeight;
  textArea.value = "";
}

// Adjusting time format for chat window
function timeFormat(time) {
  if (typeof time === "string") {
    time = Date.parse(time);
    time = new Date(time);
  }
  const chatTime = new Date();
  if (
    time.getFullYear() === chatTime.getFullYear() &&
    time.getMonth() === chatTime.getMonth() &&
    time.getDate() === chatTime.getDate()
  ) {
    return time.getHours() + ":" + addingZero(time.getMinutes()) + ", Today";
  } else {
    if (time.getFullYear() === chatTime.getFullYear()) {
      return (
        time.getHours() +
        ":" +
        addingZero(time.getMinutes()) +
        ", " +
        time.getDate() +
        ". " +
        (time.getMonth() + 1) +
        "."
      );
    } else {
      return (
        time.getHours() +
        ":" +
        addingZero(time.getMinutes()) +
        ", " +
        time.getDate() +
        ". " +
        (time.getMonth() + 1) +
        ". " +
        time.getFullYear()
      );
    }
  }
}

// Creates room id from users ids
function getRoomIdFromUsersIds(otherUser) {
  if (currentUser < otherUser) {
    return currentUser.toString() + "-" + otherUser.toString();
  } else {
    return otherUser.toString() + "-" + currentUser.toString();
  }
}

// Decodes users ids from room id
function decodeRoomIdToUsers(roomId) {
  const splitted = roomId.split("-");
  if (Number(splitted[0]) === currentUser) {
    return splitted[1];
  } else {
    return splitted[0];
  }
}

// Sends GET response and draws chat history
function getChatHistory(id) {
  var requestOptions = {
    method: "GET",
    headers: { "Content-Type": "application/json", "Other-User": id },
    redirect: "follow",
  };
  fetch("/get_chat_history", requestOptions)
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        response.json().then((data) => {
          chat.innerHTML = "";
          data.forEach((element) => {
            if (element.from_user === currentUser) {
              chat.innerHTML += newMessageMe(
                timeFormat(element.time),
                element.body
              );
            } else if (element.to_user === currentUser) {
              chat.innerHTML += newMessageYou(
                String(element.from_user),
                timeFormat(element.time),
                element.body
              );
            } else {
              console.log(
                "Skipped msg: " + element.body,
                element.to_user,
                element.from_user
              );
            }
          });
          chat.scrollTop = chat.scrollHeight;
        });
      }
    })
    .catch(function (e) {
      console.log(e);
    });
}
