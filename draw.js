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
  body.html(`
    dogs
  `);
}

let start = function() {
  $("body")
    .html(
      emptydiv("nav") +
      emptydiv("body")
    );
  makenav()
  makebod()
};

$(start);

