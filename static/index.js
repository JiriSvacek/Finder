const pageLoader = document.getElementById("pageloader");

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(log_it, notAcepted);
    pageLoader.classList.add("is-active");
  } else {
    console.log("No location");
  }
}

// Sends POST location.
function log_it(position) {
  let data = {
    lat: position.coords.latitude,
    long: position.coords.longitude,
  };
  fetch("/cords", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => {
      pageLoader.classList.remove("is-active");
      if (response.redirected) {
        window.location.href = response.url;
      }
    })
    .catch(function (e) {
      pageLoader.getElementsByTagName("span").valueinnerHTML = e;
      console.log(e);
      setTimeout(() => {
        pageLoader.classList.remove("is-active");
      }, "3000");
    });
}

function notAcepted() {
  pageLoader.classList.remove("is-active");
  document.getElementById("war").innerHTML =
    '<div class="column is-one-third notification is-danger">We need your location!</div>';
}
