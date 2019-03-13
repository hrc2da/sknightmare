class DiningRoom {
    constructor(w, h, padding) {
        this.tables = [];
        this.num_tables = 0;
        this.items = [];
        this.num_items = 0;
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
        table_data.name = "Table " + dining_room.num_tables;
        table["data"] = table_data;

        let added_table = new Table(
            table["table_svg_attrs"]["svg_type"],
            "Table " + dining_room.num_tables,
            table_data["num_seats"],
            table_data["size"],
            table_data["cost"],
            table_data["daily_upkeep"],
            table_data["x"],
            table_data["y"]
        );
        let table_svg_attrs = added_table.draw();
        table_data = table_svg_attrs["data"][0];
        // add drag handling to the table object
        let drag = d3
            .drag()
            .on("drag", function (d) {
                d3.select(this)
                    .select(table_svg_attrs["svg_type"])
                    .attrs(table_svg_attrs["shape_drag_attrs"]);
                d3.select(this)
                    .select("text")
                    .attrs(table_svg_attrs["text_drag_attrs"]);
            })
            .on("end", function (d) {
                let mouseX = d3.mouse(this)[0];
                let mouseY = d3.mouse(this)[1];
                let dining_bound_box = d3.select("#dining_layout");
                let x_min = Number(dining_bound_box.attr("x"));
                let y_min = Number(dining_bound_box.attr("y"));
                let x_max = x_min + Number(dining_bound_box.attr("width"));
                let y_max = y_min + Number(dining_bound_box.attr("height"));

                if (mouseX > x_max || mouseX < x_min || mouseY < y_min || mouseY > y_max) {
                    d3.select(this).remove();
                }
            });

        table_g.call(drag);

        //update table tracking
        this.num_tables++;
        this.tables.push(table);
    };

    add_item = item => {
        // all the disparate places where there is table information
        let item_g = item["item_g"];
        let item_data = item["item_svg_attrs"]["data"][0];
        item["data"] = item_data;
        let added_item = new Item(
            item['item_svg_attrs']["svg_type"],
            item_data["name"] + " " + dining_room.num_items,
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
            .on("drag", function (d) {
                d3.select(this)
                    .select(item_svg_attrs["svg_type"])
                    .attrs(item_svg_attrs["shape_drag_attrs"]);
                d3.select(this)
                    .select("text")
                    .attrs(item_svg_attrs["text_drag_attrs"]);
            })
            .on("end", function (d) {
                let mouseX = d3.mouse(this)[0];
                let mouseY = d3.mouse(this)[1];
                let dining_bound_box = d3.select("#dining_layout");
                let x_min = Number(dining_bound_box.attr("x"));
                let y_min = Number(dining_bound_box.attr("y"));
                let x_max = x_min + Number(dining_bound_box.attr("width"));
                let y_max = y_min + Number(dining_bound_box.attr("height"));

                if (mouseX > x_max || mouseX < x_min || mouseY < y_min || mouseY > y_max) {
                    d3.select(this).remove();
                }
            });

        item_g.call(drag);

        //update table tracking
        this.num_items++;
        this.items.push(item);
    };

    // export the current layout as a list of json objects
    get_layout = () => {
        let dining_bound_box = d3.select("#dining_layout");
        let x_min = Number(dining_bound_box.attr("x"));
        let y_min = Number(dining_bound_box.attr("y"));
        let x_max = x_min + Number(dining_bound_box.attr("width"));
        let y_max = y_min + Number(dining_bound_box.attr("height"));

        let table_layout = [];
        for (let table of this.tables) {
            let table_repr = {};
            table_repr["x"] = table["data"].x;
            table_repr["y"] = table["data"].y;
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
            table_layout.push(table_repr);
        }
        let equipment_layout = [];
        for (let eq of this.items) {
            let eq_repr = {};
            eq_repr["name"] = eq["data"].name;
            eq_repr["attributes"] = eq["data"].attributes;
            eq_repr["attributes"]["x"] = eq["data"]["x"];
            eq_repr["attributes"]["y"] = eq["data"]["y"];
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
        return {
            tables: table_layout,
            equipment: equipment_layout
        };
    };
}