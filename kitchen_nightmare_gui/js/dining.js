d3.selection.prototype.moveToBack = function() {
  return this.each(function() {
    var firstChild = this.parentNode.firstChild;
    if (firstChild) {
      this.parentNode.insertBefore(this, firstChild);
    }
  });
};

class DiningRoom {
  constructor(w, h, padding) {
    this.tables = [];
    this.table_id_counter = 0;
    this.items = [];
    this.item_id_counter = 0;
    this.num_waiters = 0;
    this.waiters = [];
    this.width = w;
    this.height = h;
    this.padding = padding;
  }

  // adds a table to the center of the dining table such that the user can drag it around the dining room
  add_table = table => {
    // all the disparate places where there is table information
    // let table_svg_attrs = table['table_svg_attrs'];
    let table_g = table["table_g"];
    let table_data = table["table_svg_attrs"]["data"][0];
    table_data.name = "Table " + dining_room.table_id_counter;
    table["data"] = table_data;
    console.log("Table", table_data["noisiness"], table_data);
    let added_table = new Table(
      table["table_svg_attrs"]["svg_type"],
      "Table " + dining_room.table_id_counter,
      table_data["attributes"]["seats"],
      table_data["size"],
      table_data["attributes"]["cost"],
      table_data["attributes"]["daily_upkeep"],
      table_data["x"],
      table_data["y"],
      table_data["svg_path"],
      table_data["attributes"]["noisiness"],
      table_data["attributes"]["appliances"]
    );

    let taper = 10;
    for (let i = 1; i <= taper; i++) {
      table_g
        .selectAll(".table_bounds_" + i)
        .data([table_data])
        .enter()
        .append("circle")
        .attrs({
          cx: d => {
            return d.x;
          },
          cy: d => {
            return d.y;
          },
          class: "table_bounds",
          r: 3 * added_table.size * (i / taper),
          fill: "red",
          opacity: 0.1,
          "pointer-events": "none"
        })
        .moveToBack();
    }

    let table_svg_attrs = added_table.draw();
    table_data = table_svg_attrs["data"][0];
    // add drag handling to the table object
    let drag = d3
      .drag()
      .on("drag", function(d) {
        d3.select(this.parentNode)
          .select(table_svg_attrs["svg_type"])
          .attrs(table_svg_attrs["shape_drag_attrs"]);
        d3.select(this.parentNode)
          .select("text")
          .attrs(table_svg_attrs["text_drag_attrs"]);
        d3.select(this.parentNode)
          .selectAll("circle")
          .moveToBack()
          .attrs(table_svg_attrs["bounds_drag_attrs"]);
      })
      .on("end", function(d) {
        let mouseX = d3.mouse(this)[0];
        let mouseY = d3.mouse(this)[1];
        let dining_bound_box = d3.select("#dining_layout");
        let x_min = Number(dining_bound_box.attr("x"));
        let y_min = Number(dining_bound_box.attr("y"));
        let x_max = x_min + Number(dining_bound_box.attr("width"));
        let y_max = y_min + Number(dining_bound_box.attr("height"));

        if (
          mouseX > x_max ||
          mouseX < x_min ||
          mouseY < y_min ||
          mouseY > y_max
        ) {
          console.log(this.parentNode);
          d3.select(this.parentNode).remove();
        }
      });

    table_g.select("image").call(drag);
    table_g.select("image").on("dblclick", (d, i, node) => {
      let bbox = node[i].getBBox();
      let x_center = bbox.x + bbox.width / 2;
      let y_center = bbox.y + bbox.height / 2;
      let rot = d3.select(node[i]).attr("rot");
      if (rot == undefined) {
        rot = 0;
      } else {
        rot = parseInt(rot);
      }
      rot += 90;
      d3.select(node[i])
        .attr(
          "transform",
          "rotate(" + rot + "," + x_center + "," + y_center + ")"
        )
        .attr("rot", rot);
    });
    //update table tracking

    this.table_id_counter++;
    this.tables.push(table);
  };

  add_item = item => {
    // all the disparate places where there is table information
    let item_g = item["item_g"];
    let item_data = item["item_svg_attrs"]["data"][0];
    item["data"] = item_data;
    let added_item = new Item(
      item["item_svg_attrs"]["svg_type"],
      item_data["name"] + " " + dining_room.item_id_counter,
      item_data["size"],
      item_data["attributes"],
      item_data["x"],
      item_data["y"]
    );
    let item_svg_attrs = added_item.draw();
    item_data = item_svg_attrs["data"][0];
    // add drag handling to the table object
    let drag = d3
      .drag()
      .on("drag", function(d) {
        d3.select(this)
          .select(item_svg_attrs["svg_type"])
          .attrs(item_svg_attrs["shape_drag_attrs"]);
        // d3.select(this)
        //   .select("text")
        //   .attrs(item_svg_attrs["text_drag_attrs"]);
      })
      .on("end", function(d) {
        let mouseX = d3.mouse(this)[0];
        let mouseY = d3.mouse(this)[1];
        let dining_bound_box = d3.select("#dining_layout");
        let x_min = Number(dining_bound_box.attr("x"));
        let y_min = Number(dining_bound_box.attr("y"));
        let x_max = x_min + Number(dining_bound_box.attr("width"));
        let y_max = y_min + Number(dining_bound_box.attr("height"));

        if (
          mouseX > x_max ||
          mouseX < x_min ||
          mouseY < y_min ||
          mouseY > y_max
        ) {
          d3.select(this).remove();
        }
      });

    item_g.call(drag);

    item_g.select("image").on("dblclick", (d, i, node) => {
      let bbox = node[i].getBBox();
      let x_center = bbox.x + bbox.width / 2;
      let y_center = bbox.y + bbox.height / 2;
      let rot = d3.select(node[i]).attr("rot");
      if (rot == undefined) {
        rot = 0;
      } else {
        rot = parseInt(rot);
      }
      rot += 90;
      d3.select(node[i])
        .attr(
          "transform",
          "rotate(" + rot + "," + x_center + "," + y_center + ")"
        )
        .attr("rot", rot);
    });

    //update table tracking
    this.item_id_counter++;
    this.items.push(item);
  };

  add_staff = waiter => {
    // all the disparate places where there is table information
    let waiter_g = waiter["waiter_g"];
    let waiter_data = waiter["waiter_svg_attrs"]["data"][0];
    waiter["data"] = waiter_data;
    let added_waiter = new Staff(waiter_data["x"], waiter_data["y"]);

    let taper = 10;
    for (let i = 1; i <= taper; i++) {
      waiter_g
        .selectAll(".waiter_bounds_" + i)
        .data([waiter_data])
        .enter()
        .append("circle")
        .attrs({
          cx: d => {
            return d.x + added_waiter.size / 2;
          },
          cy: d => {
            return d.y + added_waiter.size / 2;
          },
          class: "waiter_bounds",
          r: added_waiter.range * (i / taper),
          fill: "steelblue",
          opacity: 0.1,
          "pointer-events": "none"
        })
        .moveToBack();
    }

    let waiter_svg_attrs = added_waiter.draw();
    waiter_data = waiter_svg_attrs["data"][0];

    // add drag handling to the table object
    let drag = d3
      .drag()
      .on("drag", function(d) {
        d3.select(this.parentNode)
          .select(waiter_svg_attrs["svg_type"])
          .attrs(waiter_svg_attrs["shape_drag_attrs"]);
        d3.select(this.parentNode)
          .selectAll("circle")
          .moveToBack()
          .attrs(waiter_svg_attrs["bounds_drag_attrs"]);
      })
      .on("end", function(d) {
        let mouseX = d3.mouse(this)[0];
        let mouseY = d3.mouse(this)[1];
        let dining_bound_box = d3.select("#dining_layout");
        let x_min = Number(dining_bound_box.attr("x"));
        let y_min = Number(dining_bound_box.attr("y"));
        let x_max = x_min + Number(dining_bound_box.attr("width"));
        let y_max = y_min + Number(dining_bound_box.attr("height"));

        if (
          mouseX > x_max ||
          mouseX < x_min ||
          mouseY < y_min ||
          mouseY > y_max
        ) {
          d3.select(this.parentNode).remove();
        }
      });
    waiter_g.select("image").call(drag);

    //update table tracking
    this.num_waiters++;
    this.waiters.push(waiter);
  };

  clear_layout = () => {
    for (let table of this.tables) {
      table["table_g"].remove();
    }
    for (let item of this.items) {
      item["item_g"].remove();
    }
    for (let waiter of this.waiters) {
      waiter["waiter_g"].remove();
    }
    this.item_id_counter = 0;
    this.table_id_counter = 0;
    this.num_waiters = 0;
    this.tables = [];
    this.items = [];
    this.waiters = [];
  };
  /*
        type,
        name,
        seats,
        size,
        cost,
        upkeep,
        x,
        y,
        svg_path,
    */
  load_json_layout = json_string => {
    this.clear_layout();
    let dining_repr = JSON.parse(json_string);
    let table_info = dining_repr["tables"];
    let item_info = dining_repr["equipment"];
    let waiter_info = dining_repr["waiters"];

    let svg = d3.select("#gui_layout");
    for (let table of table_info) {
      let table_obj = new Table(
        "image",
        table["name"],
        table["attributes"]["seats"],
        table["attributes"]["radius"],
        table["attributes"]["cost"],
        table["attributes"]["daily_upkeep"],
        table["attributes"]["x"] * this.width,
        table["attributes"]["y"] * this.height,
        table["attributes"]["svg_path"],
        table["attributes"]["noisiness"],
        table["attributes"]["appliances"]
      );
      let svg_attrs = table_obj.draw();

      let group = svg.append("g").attrs({
        id: "new_table_" + dining_room.table_id_counter
      });

      // add the placeholder icons
      group
        .selectAll(".new_table_icon")
        .data(svg_attrs["data"])
        .enter()
        .append(svg_attrs["svg_type"])
        .attrs(svg_attrs["shape_attrs"]);

      // add placeholder text
      group
        .selectAll(".new_table_text")
        .data(svg_attrs["data"])
        .enter()
        .append("text")
        .text(svg_attrs["text"])
        .attrs(svg_attrs["text_attrs"]);

      this.add_table({
        table_svg_attrs: svg_attrs,
        table_g: group
      });
    }

    for (let item of item_info) {
      let item_obj = new Item(
        "image",
        item["name"],
        35,
        item["attributes"],
        Math.random() * this.width,
        Math.random() * this.height
      );
      console.log(item_obj);
      let svg_attrs = item_obj.draw();
      let group = svg.append("g").attrs({
        id: "new_item_" + dining_room.item_id_counter
      });

      // add the placeholder icons
      group
        .selectAll(".new_item_icon")
        .data(svg_attrs["data"])
        .enter()
        .append(svg_attrs["svg_type"])
        .attrs(svg_attrs["shape_attrs"]);

      // add placeholder text
      group
        .selectAll(".new_item_text")
        .data(svg_attrs["data"])
        .enter()
        .append("text")
        .text(svg_attrs["text"])
        .attrs(svg_attrs["text_attrs"]);

      this.add_item({
        item_svg_attrs: svg_attrs,
        item_g: group
      });
    }
    for (let waiter of waiter_info) {
      let staff_obj = new Staff(
        waiter["x"] * this.width,
        waiter["y"] * this.height
      );
      let svg_attrs = staff_obj.draw();

      let group = svg.append("g").attrs({
        id: "waiter_" + this.num_waiters
      });

      // add the placeholder icons
      group
        .selectAll(".new_waiter_icon")
        .data(svg_attrs["data"])
        .enter()
        .append(svg_attrs["svg_type"])
        .attrs(svg_attrs["shape_attrs"]);

      // add placeholeder text
      group
        .selectAll(".new_waiter_text")
        .data(svg_attrs["data"])
        .enter()
        .append("text")
        .text(svg_attrs["text"])
        .attrs(svg_attrs["text_attrs"]);

      this.add_staff({
        waiter_svg_attrs: svg_attrs,
        waiter_g: group
      });
    }
  };

  // export the current layout as a list of json objects
  get_layout = () => {
    let dining_bound_box = d3.select("#dining_layout");
    let x_min = Number(dining_bound_box.attr("x")) / this.width;
    let y_min = Number(dining_bound_box.attr("y")) / this.height;
    let x_max = (x_min + Number(dining_bound_box.attr("width"))) / this.width;
    let y_max = (y_min + Number(dining_bound_box.attr("height"))) / this.height;

    let table_layout = [];
    let equipment_layout = [];
    for (let table of this.tables) {
      let table_repr = {};
      table_repr["x"] = table["data"].x / this.width;
      table_repr["y"] = table["data"].y / this.height;
      // not on the table so continue
      if (
        table_repr["x"] > x_max ||
        table_repr["x"] < x_min ||
        table_repr["y"] < y_min ||
        table_repr["y"] > y_max
      ) {
        continue;
      }
      table_repr["size"] = table["data"].size;
      table_repr["seats"] = table["data"]["attributes"].seats;
      table_repr["type"] = table["data"]["attributes"].type;
      table_repr["cost"] = table["data"]["attributes"].cost;
      table_repr["daily_upkeep"] = table["data"]["attributes"].daily_upkeep;
      table_repr["name"] = table["data"].name;
      table_repr["attributes"] = table["data"].attributes;
      table_repr["attributes"]["x"] = table_repr["x"];
      table_repr["attributes"]["y"] = table_repr["y"];
      table_repr["attributes"]["noisiness"] =
        table["data"]["attributes"].noisiness;
      table_layout.push(table_repr);

      if (table["data"].attributes.appliances.length > 0) {
        console.log(table);
        for (let a of table["data"].attributes.appliances) {
          a["attributes"]["x"] = table_repr["attributes"]["x"];
          a["attributes"]["y"] = table_repr["attributes"]["y"];
          equipment_layout.push(a);
        }
      }
    }

    for (let eq of this.items) {
      let eq_repr = {};
      eq_repr["name"] = eq["data"].name;
      eq_repr["attributes"] = eq["data"].attributes;
      eq_repr["attributes"]["x"] = eq["data"]["x"] / this.width;
      eq_repr["attributes"]["y"] = eq["data"]["y"] / this.height;
      // not on the table so continue
      if (
        eq_repr["attributes"]["x"] > x_max ||
        eq_repr["attributes"]["x"] < x_min ||
        eq_repr["attributes"]["y"] < y_min ||
        eq_repr["attributes"]["y"] > y_max
      ) {
        continue;
      }
      equipment_layout.push(eq_repr);
    }
    let staff_layout = [];
    for (let waiter of this.waiters) {
      let waiter_repr = {};
      waiter_repr["x"] = waiter["data"]["x"] / this.width;
      waiter_repr["y"] = waiter["data"]["y"] / this.height;
      // not on the table so continue
      if (
        waiter_repr["x"] > x_max ||
        waiter_repr["x"] < x_min ||
        waiter_repr["y"] < y_min ||
        waiter_repr["y"] > y_max
      ) {
        continue;
      }
      staff_layout.push(waiter_repr);
    }
    return {
      tables: table_layout,
      equipment: equipment_layout,
      staff: staff_layout
    };
  };
}
