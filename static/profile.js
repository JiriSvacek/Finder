// Sends GET response and receive person for possible match
async function give_available() {
  const parsed = await send_response("available");
  if (parsed["missing_values"]) {
    draw_problem(parsed["missing_values"]);
  } else {
    draw_user(parsed);
  }
}

// Sent GET response "match" or "swipe"
async function user_vote(address) {
  const parsed = await send_response(address);
  if (parsed["missing_values"]) {
    draw_problem(parsed["missing_values"]);
  } else {
    give_available();
  }
}

function send_response(address) {
  return fetch("/" + address)
    .then((response) => {
      if (response.redirected) {
        return (window.location.href = response.url);
      } else {
        return response.text().then(function (text) {
        console.log(text)
          return JSON.parse(text);
        });
      }
    })
    .catch(function (e) {
      console.log(e);
    });
}

function calculate_age(time) {
  const value = new Date(Date.parse(time));
  return new Date().getFullYear() - value.getFullYear();
}

function basic_picture() {
  document.getElementById("pic").src = "static/basePhotoWP.jpg";
}

function draw_user(data) {
  document.getElementById("user").innerHTML =
    '<div class="column is-6 is-offset-3">' +
    '<div class="box">' +
    '<h2 class="title is-2 has-text-black has-text-left">' +
    data.name +
    "</h2>" +
    '<figure class="image is-4by3">' +
    '<img id="pic" src="' +
    data.image +
    '" onerror="basic_picture()"' +
    ">" +
    "</figure>" +
    '<div class="columns has-text-left">' +
    '<div class="column is-3">' +
    '<h3 class="title is-3 has-text-black ">Age:</h3>' +
    "</div>" +
    '<div class="column is-one-third">' +
    '<h3 class="subtitle is-3 has-text-black">' +
    calculate_age(data.birthday) +
    "</h3>" +
    "</div>" +
    "</div>" +
    '<div class="columns has-text-left">' +
    '<div class="column is-3">' +
    '<h3 class="title is-3 has-text-black">Gender:</h3>' +
    "</div>" +
    '<div class="column is-one-third">' +
    '<h3 class="subtitle is-3 has-text-black">' +
    data.gender +
    "</h3>" +
    "</div>" +
    "</div>" +
    '<div class="columns">' +
    '<div class="column">' +
    `<button onclick="user_vote('match')" class="button is-primary is-large is-fullwidth">Match</button>` +
    "</div>" +
    '<div class="column">' +
    `<button onclick="user_vote('swipe')" class="button is-danger is-large is-fullwidth">Swipe</button>` +
    "</div>" +
    "</div>" +
    "</div>" +
    "</div>" +
    "</div>";
}

// If there is issue function draws message
function draw_problem(data) {
  document.getElementById("user").innerHTML =
    '<div class="columns is-centered">' +
    '<div class="column is-3 is-centered">' +
    '<div class="notification is-danger">' +
    data +
    "</div>" +
    "</div>" +
    "</div>";
}


give_available();

