function setupRestaurant(w, h) {
    let padding = 5;
    // define the window
    let svg = d3.select("#window")
        .append("svg")
        .attrs({
            id: "gui_layout",
            width: w,
            height: h,
        });

    // bounding for kitchen
    let dining_width = w * 0.7;
    let dining_height = h * 0.7;
    svg.append('rect').attrs({
        id: "dining_layout",
        x: padding,
        y: padding,
        width: dining_width,
        height: dining_height,
        fill: "none",
        "stroke-width": 2,
        stroke: "black"
    });

    let dining_room = new DiningRoom(dining_width, dining_height);

    // selection pane for tables
    let table_box_width = w * 0.7;
    let table_box_height = h * 0.2;
    let table_box_x = padding;
    let table_box_y = dining_height + padding
    svg.append('rect').attrs({
        id: "selection_layout",
        x: table_box_x,
        y: table_box_y,
        width: table_box_width,
        height: table_box_height,
        fill: "none",
        "stroke-width": 2,
        stroke: "black"
    });

    //marketplace panel
    let marketplace_width = w * 0.2;
    let marketplace_height = h * 0.9;
    let marketplace_x = dining_width + padding;
    let marketplace_y = padding
    svg.append('rect').attrs({
        id: "marketplace_layout",
        x: marketplace_x,
        y: marketplace_y,
        width: marketplace_width,
        height: marketplace_height,
        fill: "none",
        "stroke-width": 2,
        stroke: "black"
    });

    // make placeholder tables
    let placeholder_tables = [];
    d3.json("data/tables.json").then(function (data) {
        let increment = table_box_width / Object.keys(data).length;
        let x = table_box_x + padding * 7;
        let y = table_box_y + padding * 10;
        for (let key in data) {
            let table_data = data[key];
            let table = new Table(table_data['type'], table_data['seats'], table_data['size'], x, y);
            let svg_attrs = table.draw();

            let group = svg.append("g").attrs({
                id: 'placeholder_table_' + key
            })

            // add the placeholder icons 
            group.selectAll(".place_holder_table_icon")
                .data(svg_attrs['data'])
                .enter()
                .append(svg_attrs['svg_type'])
                .attrs(svg_attrs['shape_attrs']);

            // add placeholeder text
            group.selectAll(".place_holder_table_text")
                .data(svg_attrs['data'])
                .enter()
                .append("text")
                .text(svg_attrs['text'])
                .attrs(svg_attrs['text_attrs'])

            // when a placeholder is clicked it creates a new table in the middle of the dining room 
            // uses DiningRoom.add_table to insert it to the dining room
            group.on("click", () => {
                let added_table = new Table(table_data['type'], table_data['seats'], table_data['size'], dining_room.width / 2, dining_room.height / 2)
                let added_table_svg_attrs = added_table.draw();
                // make a group for the visual table elements
                let added_table_g = svg.append("g").attrs({
                    id: 'table_' + dining_room.num_tables
                })
                // draw the table
                added_table_g.selectAll('.table_icon')
                    .data(added_table_svg_attrs['data'])
                    .enter()
                    .append(added_table_svg_attrs['svg_type'])
                    .attrs(added_table_svg_attrs['shape_attrs']);
                added_table_g.selectAll('.table_text')
                    .data(added_table_svg_attrs['data'])
                    .enter()
                    .append("text")
                    .text(added_table_svg_attrs['text'])
                    .attrs(added_table_svg_attrs['text_attrs'])

                // add the table to the dining room this all should likely be part of the dining room class but this will
                // be done tomorrow <<<<<<<< DO THIS
                dining_room.add_table({
                    'table': added_table,
                    'table_svg_attrs': added_table_svg_attrs,
                    'table_g': added_table_g
                })
            })

            placeholder_tables.push(table);
            x += increment;
        }

    });

    return dining_room;
}