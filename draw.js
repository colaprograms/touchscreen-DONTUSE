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

let set_body_to_text = function(text) {
  $("#bodydraw").html("<pre id='bodydrawtext'></pre>")
  $("#bodydrawtext").text(text);
}

let set_book = function(data) {
  /* data format:
   *
   * error 1:
   * {
   *   error: ["http", code, reason, headers]
   * }
   *
   * error 2: record.py threw an exception while parsing stuff
   * {
   *   error: ["parsing", (traceback)]
   * }
   *
   * success:
   * {
   *   error: None
   *   fields: [["dog", ["fantastic dog"]], ["frog", ["frog, tolerable"]]],
   * }
   */
  if(data.error) {
    if(data.error[0] == "http") {
      makeerror_http(data);
    }
    else if(data.error[0] == "parsing") {
      makeerror_parsing(data);
    }
    else {
      set_body_to_text(`Unknown error type:\n\n${JSON.stringify(data)}`);
      $("#bodydraw_json").text(JSON.stringify(data));
    }
  }
  else {
    $("#bodydraw").html("<div id='fields'></div>");
    let fields = $("#fields");
    data.fields.forEach(function(field, idx) {
      let fieldob = $("<div class='field'></div>");
      fieldob.append(`<div class='fieldname'>${field[0]}</div>`);
      field[1].forEach(function(data, dataidx) {
        fieldob.append(`<div class='fielddata'>${data}</div>`);
      });
    });
  }
  $("#bodydraw").html("got successful response");
  console.log(data);
}

let showtexterror = function(status) {
  $("#bodydraw").html(`
    <div id="bodyerror">${status}</div>
  `);
}

let bookchanger = function() {
  let url = "http://localhost:9000/getrecord";
  console.log(`Loading ${url}`);
  let ajax =
    $.ajax(url)
     .done(function(data) {
       let json = JSON.parse(data);
       set_book(json);
     })
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

