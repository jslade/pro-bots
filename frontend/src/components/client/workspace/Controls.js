import { useCallback, useContext, useEffect } from 'react';

import { Grid, Button, Typography } from '@mui/material';

import { ApiContext } from '../../../contexts/ApiContext';
import { GameContext } from '../../../contexts/GameContext';

const Controls = () => {
    const api = useContext(ApiContext);
    const { player, scoresUpdated } = useContext(GameContext);

    useEffect(() => {}, [player, scoresUpdated]);
    
    const onMove = useCallback((e) => {
        const dir = e.shiftKey ? "backward" : "forward";
        api.sendMessage("manual_control", "movement", {move: dir})
    }, [api]);

    const onTurnLeft = useCallback((e) => {
        api.sendMessage("manual_control", "movement", {turn: "left"})
    }, [api]);

    const onTurnRight = useCallback((e) => {
        api.sendMessage("manual_control", "movement", {turn: "right"})
    }, [api]);

    return (
        <Grid container sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
        }} spacing={3} >
            <Grid item xs={2}>
                <Button variant="contained" onClick={onTurnLeft}>turn&nbsp;L</Button>
            </Grid>
            <Grid item xs={2}>
                <Button variant="contained" onClick={onMove}>move</Button>
            </Grid>
            <Grid item xs={2}>
                <Button variant="contained" onClick={onTurnRight}>turn&nbsp;R</Button>
            </Grid>
            <Grid item xs={2}>
                <Typography >Score: {player?.score || 0}</Typography>
            </Grid>
        </Grid>
    );
};

export default Controls;
