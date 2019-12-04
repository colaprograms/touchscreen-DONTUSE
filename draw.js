//draw.js

let emptydiv = function(id) { return `<div id="${id}"></div>`; }

let makenav = function() {
  let navigation = $("#nav");
  let navtext = "Random book display";
  navigation.html(`
    <div id="navheader">${navtext}</div>
  `);
}

let makebod = function() {
  let body = $("#body");
  console.log(body);
  body.html(
    emptydiv("bodydraw")
  );
}

let set_book = function(data) {
  $("#bodydraw").html("got successful response");
  console.log(data);
}

let showtexterror = function(status) {
  $("#bodydraw").html(`
    <div id="bodyerror">${status}</div>
  `);
}

let bookchanger = function() {
  let url = recordurl(random_rec());
  console.log(`Loading ${url}`);
  let ajax =
    $.ajax(url)
     .done(function(data) { set_book(data); })
     .fail(function(jqxhr, status, error) {
      showtexterror(status);
     });
};

let BOOKCHANGE_INTERVAL = 60000; // one minute

let bcstart = function() {
  setInterval(
    BOOKCHANGE_INTERVAL,
    bookchanger
  )
};

let start = function() {
  $("body")
    .html(
      emptydiv("nav") +
      emptydiv("body")
    );
  makenav()
  makebod()
  bcstart()
};

$(start);

