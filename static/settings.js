const lowerAgeLimit = document.getElementById("lowerAgeLimit"),
  switchGender = document.getElementById("switchGender"),
  upperAgeLimit = document.getElementById("upperAgeLimit"),
  range = document.getElementById("range"),
  outputLowerAgeLimit = document.getElementById("outputLowerAgeLimit"),
  outputRange = document.getElementById("outputRange"),
  manCheckbox = document.getElementById("manCheckbox"),
  womanCheckbox = document.getElementById("womanCheckbox"),
  outputUpperAgeLimit = document.getElementById("outputUpperAgeLimit"),
  FEMALE = "Female",
  MALE = "Male";

var actualDate = new Date(),
  posted = false,
  maximDate = new Date();

actualDate.setFullYear(actualDate.getFullYear() - 18);
maximDate.setFullYear(maximDate.getFullYear() - 18);
bulmaSlider.attach();

// Writing recivied data from DB to every row in form
if (user[0]) {
  actualDate = new Date(user[0]);
}
if (user[1]) {
  const checking = String(user[1]);
  if (checking.valueOf() === FEMALE) {
    switchGender.checked = true;
  } else {
    switchGender.checked = false;
  }
}

if (user[2]) {
  const lowerLimit = String(user[2]);
  lowerAgeLimit.value = lowerLimit;
  outputLowerAgeLimit.value = lowerLimit;
} else {
  outputLowerAgeLimit.value = lowerAgeLimit.value;
}

if (user[3]) {
  const upperLimit = String(user[3]);
  upperAgeLimit.value = upperLimit;
  outputUpperAgeLimit.value = upperLimit;
} else {
  outputUpperAgeLimit.value = upperAgeLimit.value;
}

if (user[4]) {
  const rangeLimit = String(user[4]);
  range.value = rangeLimit;
  outputRange.value = rangeLimit;
} else {
  outputRange.value = range.value;
}

if (user[5]) {
  const str = String(user[5]);
  if (str == "not a valid image url from internet") {
    picture.value = "";
    picture.placeholder = "You input " + str;
  } else {
    picture.placeholder = "Url image";
    picture.value = str;
  }
}
if (user[6]) {
  const interestedArray = user[6];
  interestedArray.forEach((element) => {
    if (element === MALE) {
      manCheckbox.checked = true;
    } else if (element === FEMALE) {
      womanCheckbox.checked = true;
    } else {
      console.log(element + " was not reccognized");
    }
  });
}

lowerAgeLimit.addEventListener("change", function () {
  var limiting_value = upperAgeLimit.value;
  if (lowerAgeLimit.value > limiting_value) {
    lowerAgeLimit.value = limiting_value;
    outputLowerAgeLimit.value = limiting_value;
  }
});

upperAgeLimit.addEventListener("change", function () {
  var limiting_value = lowerAgeLimit.value;
  if (upperAgeLimit.value < limiting_value) {
    upperAgeLimit.value = limiting_value;
    outputUpperAgeLimit.value = limiting_value;
  }
});

// Creating Bulma calendar
var calendars = bulmaCalendar.attach('[type="date"]', {
  showButtons: false,
  startDate: actualDate,
  maxDate: maximDate,
});
var element = document.querySelector("#calendar");
if (element) {
  // bulmaCalendar instance is available as element.bulmaCalendar
  element.bulmaCalendar.on("select", function (datepicker) {
    console.log(datepicker.data.value());
  });
}

function sendSettings() {
  const manCheck = manCheckbox.checked,
    womanCheck = womanCheckbox.checked;

  if (manCheck || womanCheck) {
    var data = {
      date: element.value,
      gender: getCheckboxGender(switchGender.checked),
      lowerAge: lowerAgeLimit.value,
      upperAge: upperAgeLimit.value,
      range: range.value,
      //range: String(range.value) + "asasd",
      img: picture.value,
      interest: [
        ...(womanCheck ? ["Female"] : []),
        ...(manCheck ? ["Male"] : []),
      ],
    };
    fetch("/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (response.redirected) {
          window.location.href = response.url;
        } else {
          document.location.reload();
        }
        console.log(response);
      })
      .catch(function (e) {
        console.log("Problem", e);
      });
  } else {
    if (!posted) {
      const box = document.getElementById("errorMessage"),
        message = "You need to choose at least one gender!";
      box.innerHTML =
        '<div class="notification is-danger">' + message + "</div>";
      posted = true;
    }
  }
}

function getCheckboxGender(decision) {
  if (decision) {
    return FEMALE;
  } else {
    return MALE;
  }
}
