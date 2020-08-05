// https://www.digitalocean.com/community/tutorials/an-introduction-to-jquery
// http://jsfiddle.net/mblase75/zB5fv/  - read JSON
// http://jsfiddle.net/nbyrd/XNSSR/     - connect to DB

// https://stackoverflow.com/questions/3102819/disable-same-origin-policy-in-chrome
// >> chromium-browser --disable-web-security --start-fullscreen --user-data-dir="/home/pi/capra/transferAnimation_pythonServer/"


// function printJSON(data) {
//   data.forEach(item) {
//     $(".container").append('<div>' + item + '</div>');
//   }
//   var element = $('<div class="headings"><img src="' + item.image + '">' + item.name + '</div>');
//   item.other.forEach(function(otherItem) {
//     var otherElement = $('<div class="heading"><img src="' + otherItem.image + '">' + otherItem.name + '</div>');
//     element.append(otherElement);
//   });
//   $("body").append(element);
// }


function getDBSummary() {
  $.ajax({
     type: "GET",
     url: "http://127.0.0.1:5000/hello/hi" ,
     dataType: 'json',
     jsonpCallback: 'callback',
     crossDomain: true,
     success: function (data) {
       $( ".container" ).empty();
       $(".container").append('<div>' + data.dbName + '</div>');
     }
  });
}

function getLatestTransferredPic() {
  $.ajax({
     type: "GET",
     url: "http://127.0.0.1:5000/hello/users" ,
     dataType: 'json',
     jsonpCallback: 'callback',
     crossDomain: true,
     success: function (data) {
       $( ".container" ).empty();
       $(".container").append('<div>' + "Path to Picture is: " + data.picPath + '</div>');
     }
  });
}

function testTime() {
  $.ajax({
     type: "GET",
     url: "http://127.0.0.1:5000/hello/update" ,
     dataType: 'json',
     jsonpCallback: 'callback',
     crossDomain: true,
     statusCode: {
        500: function() {
          console.log("Script exhausted");
        }
      },
     success: function (data) {
       $( ".container" ).empty();
       $(".container").append('<div>' + "Latest Update at " + data.currentTime + '</div>');
     }
  });
}


// fetchHello() {
//   // GET is the default method, so we don't need to set it
//   fetch('/hello/hi')
//      .then(function (response) {
//          return response.text();
//      }).then(function (text) {
//          console.log('GET response text:');
//          console.log(text); // Print the greeting as text
//      });
//
//   // Send the same request
//   fetch('/hello')
//      .then(function (response) {
//          return response.json(); // But parse it as JSON this time
//      })
//      .then(function (json) {
//          console.log('GET response as JSON:');
//          console.log(json); // Here’s our JSON object
//      })
// }
