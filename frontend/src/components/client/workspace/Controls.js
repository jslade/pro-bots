import { useCallback, useContext } from 'react';

import { Grid, Button } from '@mui/material';

import { ApiContext } from '../../ApiContext';

const Controls = () => {
    const api = useContext(ApiContext);

    const onMove = useCallback((e) => {
        api.sendMessage("manual_control", "movement", {move: "forward"})
    }, [api]);

    const onTurnLeft = useCallback((e) => {
        api.sendMessage("manual_control", "movement", {turn: "left"})
    }, [api]);

    const onTurnRight = useCallback((e) => {
        api.sendMessage("manual_control", "movement", {turn: "right"})
    }, [api]);

    return (
        <Grid container spacing={3}>
            <Grid item xs={2}>
                <Button variant="contained" onClick={onTurnLeft}>turn&nbsp;L</Button>
            </Grid>
            <Grid item xs={2}>
                <Button variant="contained" onClick={onMove}>move</Button>
            </Grid>
            <Grid item xs={2}>
                <Button variant="contained" onClick={onTurnRight}>turn&nbsp;R</Button>
            </Grid>
        </Grid>
    );
};

export default Controls;
