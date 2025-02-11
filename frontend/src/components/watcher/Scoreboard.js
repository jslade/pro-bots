import React, { useContext, useEffect } from 'react';

import { List, ListItem } from '@mui/material';

import {GameContext} from '../../contexts/GameContext';

const Scoreboard = () => {
    const { players, scoresUpdated } = useContext(GameContext);

    useEffect(() => {}, [players, scoresUpdated])

    const playerItem = (player) => {
        return (
            <ListItem key={player.name}>
                {player.score} - {player.name}
            </ListItem>
        )
    };

    return (
        <List>
            {players.map((player) => playerItem(player))}
        </List>
    );
};


export default Scoreboard;