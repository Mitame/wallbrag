$(document).ready(function() {
  let image_grid_container = $("#image-grid-container");
  let cur_path = decodeURIComponent(document.location.pathname.substring(1));

  $.get(
    "/api/images/list",
    {
      dir: cur_path
    },
    function(listing) {
      $.each(listing.dirs, function(index, dir) {
        image_grid_container.append(
          $("<div>")
            .addClass("directory")
            .append(
              $("<a>")
                .attr("href", encodeURIComponent(dir))
                .append([
                  $("<div>").addClass("image-container").append(
                    $("<div>").addClass("image-padder"),
                    $("<img>").attr("src", "/static/dir_icon.png")
                  ),
                  $("<p>").text(dir)
              ])
            )
        );
      });

      $.each(listing.images, function(index, img) {
        let name_parts = img.split("/");
        text = name_parts[name_parts.length - 1]

        image_grid_container.append(
          $("<div>")
            .addClass("image")
            .append(
              $("<a>")
                .attr("href", img)
                .append([
                  $("<div>").addClass("image-container").append(
                    $("<div>").addClass("image-padder"),
                    $("<img>").attr("src", "/.thumb/" + img)
                  ),
                  $("<p>").addClass("title").text(text)
                ])
            )
        );
      });
    }
  );
})
