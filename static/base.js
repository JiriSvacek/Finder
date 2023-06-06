var time;

function timer() {
  const d = new Date();

  const month = addingZero(d.getMonth() + 1),
    day = addingZero(d.getDate()),
    hour = addingZero(d.getHours()),
    minute = addingZero(d.getMinutes()),
    second = addingZero(d.getSeconds());

  time.innerHTML =
    day +
    "." +
    month +
    "." +
    d.getFullYear() +
    " " +
    " " +
    hour +
    ":" +
    minute +
    ":" +
    second;
}

function addingZero(inputValue) {
  if (inputValue < 10) {
    return "0" + inputValue;
  } else {
    return inputValue;
  }
}

function standby() {
  document.getElementById("profilePhoto").src = "static/basePhotoWP.jpg";
}

document.addEventListener("DOMContentLoaded", function (event) {
  time = document.getElementById("time");
  timer();
  setInterval(timer, 1000);
});
