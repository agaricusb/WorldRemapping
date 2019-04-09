'use strict';
// Convert NBT player data files to Journeymap waypoints

const fs = require('fs');
const nbt = require('prismarine-nbt');
const in_root = '../../real-152-server/world/players/';
const out_root = '/Applications/MultiMC.app/Contents/MacOS/instances/1.7.10s/minecraft/journeymap/data/mp/172~16~2~2~25567/waypoints/';

const x_shift = -25600;

function save_wp(name, x, y, z, r, g, b) {
  const id = name + '_' + x + ',' + y + 'z';
  const j = {
      id,
      name,
      icon: "waypoint-normal.png",
      x, y, z,
      r, g, b,
      enable: true,
      type: "Normal",
      origin: "ReiMinimap",
      dimensions: [
          0
      ]
  };
  const json_data = JSON.stringify(j, null, '  ');
  const fn = id + '.json';
  const path = out_root + fn;
  fs.writeFileSync(path, json_data);
}

fs.readdir(in_root, (err, player_fns) => {
  player_fns.forEach((player_fn) => {
    if (!player_fn.endsWith('.dat')) {
      return;
    }

    const player_name = player_fn.replace('.dat', '');

    const path = in_root + player_fn;
    fs.readFile(path, (err, data) => {
      if (err) throw err;

      nbt.parse(data, (err, data) => {
        let spawn_x = data.value.SpawnX;
        let spawn_y = data.value.SpawnY;
        let spawn_z = data.value.SpawnZ;

        if (spawn_x === undefined || spawn_y === undefined || spawn_z === undefined) {
          // No spawn for this player
        } else {
          spawn_x = spawn_x.value;
          spawn_y = spawn_y.value;
          spawn_z = spawn_z.value;
        }

        let [x, y, z] = data.value.Pos.value.value;
        x = Math.round(x)|0;
        y = Math.round(y)|0;
        z = Math.round(z)|0;
  
        x += x_shift;
        if (spawn_x !== undefined) spawn_x += x_shift;

        console.log(player_name,x,y,z,spawn_x,spawn_y,spawn_z);

        save_wp('[152] Logout: ' + player_name, x, y, z, 173, 216, 230);
        if (spawn_x !== undefined && spawn_y !== undefined && spawn_z !== undefined) {
          save_wp('[152] Spawn: ' + player_name, x, y, z, 16, 210, 16);
        }
      });
    });
  });
});
