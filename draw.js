//draw.js

let emptydiv = function(id) { return `<div id="${id}"></div>`; }

var lcars_count = 0;

var LCARS_LIMIT = 20;

let add_lcars_reference = function(text) {
  let lcarslist = $("#lcarslist");

  lcars_count++
  if(lcars_count > LCARS_LIMIT)
    lcarslist.children().last().remove();

  lcarslist.children().first().removeClass("lcarscurren");

  let lcarsnew = $(`<div class='lcarsoutput'></div>`);
  lcarsnew.text(text)

  lcarsnew.addClass("lcarscurren");
  
  lcarslist.prepend(lcarsnew);
}


let makenav = function() {
  let navigation = $("#nav");
  let navtext = "RANDOM BOOK";
  navigation.html(`
    <div id="navheader">${navtext}</div>
    <div id="lcarslist"></div>
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
  else if(data.fields.length == 0) {
    retrysoon = true;
    add_lcars_reference(`${data.recordnumber} [INVALID]`);
  }
  else {
    $("#bodydraw").html("<div id='fields'></div>");
    let fields = $("#fields");
    data.fields.forEach(function(field, idx) {
      console.log(field);
      let fieldob = $("<div class='field'></div>");
      fieldob.append(`<div class='fieldname'>${field[0]}</div>`);
      field[1].forEach(function(data, dataidx) {
        fieldob.append(`<div class='fielddata'>${data}</div>`);
      });
      fields.append(fieldob)
    });
    add_lcars_reference(`${data.recordnumber}`);
  }
  console.log(data);
}

let showtexterror = function(status) {
  $("#bodydraw").html(`
    <div id="bodyerror">${status}</div>
  `);
}

var retrysoon = false;
var seconds = 999;
var BOOKCHANGE_INTERVAL = 60;
var RETRY_INTERVAL = 10;

let bookchanger = function() {
  seconds++;

  if(retrysoon)
    timeout = RETRY_INTERVAL;
  else
    timeout = BOOKCHANGE_INTERVAL;
  if(seconds < timeout)
    return;

  seconds = 0;

  retrysoon = false;

  let url = "/getrecord"; //let url = "http://localhost:9000/getrecord";

  console.log(`Loading ${url}`);

  let ajax =
    $.ajax(url)
     .done(function(data) { set_book(data) })
     .fail(function(jqxhr, status, error) {
      showtexterror(status);
     });
};

let bcstart = function() {
  setTimeout(bookchanger, 0);
  setInterval(bookchanger, 1000);
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

