import React, { useContext, useEffect } from 'react';

import { List, ListItem } from '@mui/material';

import {GameContext} from '../../contexts/GameContext';
import { Color } from 'three';

const Scoreboard = () => {
    const { players, scoresUpdated } = useContext(GameContext);

    useEffect(() => {}, [players, scoresUpdated])

    const playerItem = (player) => {
        let displayName = player.displayName;
        if (player.displayName !== player.name) {
            displayName = `${player.displayName} (${player.name})`;
        }
        return (
            <ListItem key={player.name}>
                <ColorPattern colors={player.colors} />
                <div>
                &nbsp;: {player.score} : {displayName}
                </div>
            </ListItem>
        )
    };

    return (
        <List>
            {players.map((player) => playerItem(player))}
        </List>
    );
};

const ColorPattern = ({colors}) => {
    const squareStyle = {
      width: '20px',
      height: '20px',
      border: `4px solid ${colors?.body || 'black'}`,
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gridTemplateRows: '1fr 1fr',
    };
  
    const cellStyle = {
      width: '100%',
      height: '100%',
    };
  
    return (
      <div style={squareStyle}>
        <div style={{ ...cellStyle, backgroundColor: colors?.head || 'grey' }}></div>
        <div style={{ ...cellStyle, backgroundColor: colors?.tail || 'white' }}></div>
        <div style={{ ...cellStyle, backgroundColor: colors?.tail || 'grey' }}></div>
        <div style={{ ...cellStyle, backgroundColor: colors?.head || 'white' }}></div>
      </div>
    );
  };
  

export default Scoreboard;