const api = "&APPID=b70b8c7ee4ce549fc371c07a3f7b8204";
const apiurl = "http://api.openweathermap.org/data/2.5/weather?units=metric&q=";
const searchBox = document.querySelector(".search input");
const searchBtn = document.querySelector(".search button");
const weatherIcon = document.querySelector(".weather-icon");

async function checkWeather(city) {
  const response = await fetch(apiurl + city + api);
  if (response.status == 404) {
    document.querySelector(".error").style.display = "block";
    document.querySelector(".weather").style.display = "none";
  } else {
    const data = await response.json();
    document.querySelector(".city").innerHTML = data.name;
    document.querySelector(".temp").innerHTML = Math.round(data.main.temp) + "°C";
    document.querySelector(".humidity").innerHTML = data.main.humidity + "%";
    document.querySelector(".wind").innerHTML = data.wind.speed + "km/h";
    if (data.weather[0].main == "Clouds") {
      weatherIcon.src = "C:\\Users\\lenovo\\Pictures\\Screenshots\\Screenshot (4242).png";
    } else if (data.weather[0].main == "Rain") {
      weatherIcon.src = "C:\\Users\\lenovo\\Pictures\\Screenshots\\Screenshot (4242).png";
    } else if (data.weather[0].main == "Clear") {
      weatherIcon.src = "C:\\Users\\lenovo\\Pictures\\Screenshots\\Screenshot (4242).png";
    } else if (data.weather[0].main == "Drizzle") {
      weatherIcon.src = "C:\\Users\\lenovo\\Pictures\\Screenshots\\Screenshot (4242).png";
    } else if (data.weather[0].main == "Mist") {
      weatherIcon.src = "C:\\Users\\lenovo\\Pictures\\Screenshots\\Screenshot (4242).png";
    }
    document.querySelector(".weather").style.display = "block";
    document.querySelector(".error").style.display = "none";
  }
}

searchBtn.addEventListener("click", () => {
  checkWeather(searchBox.value);
});
