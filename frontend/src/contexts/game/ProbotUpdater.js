import React, { useCallback, useContext, useEffect } from 'react';

import { ApiContext } from '../ApiContext';

const ProbotUpdater = ({ probots, setProbotsUpdated }) => {
    const api = useContext(ApiContext);

    const handleUpdateProbot = useCallback((update) => {
        if (!probots) return;

        // Update the score of the specific player
        for (const probot of probots) {
            if (probot.name === update.name) {
                Object.assign(probot, update)
                break;
            }
        }

        setProbotsUpdated(Date.now());
    }, [probots, setProbotsUpdated]);

    useEffect(() => {
        if (!api) return;

        api.registerCallback('game', 'update_probot', (data) => {
            handleUpdateProbot(data);
        });
    }, [api, api?.registerCallback, handleUpdateProbot, probots]);



    return ( <></> );
};

export { ProbotUpdater };