import React from 'react'
import PlotContainer from '../containers/PlotContainer'

import styles from "./Source.css";


const Source = ({ ra, dec, red_shift, id }) => {
  if (id === undefined) {
    return <div>Source not found</div>
  } else {
    return (
      <div className={styles.source}>
        <div className={styles.name}>{id}</div>

        <b>Location:</b> {ra}, {dec}<br/>
        <b>Red Shift: </b>{red_shift}

        <br/>
        <b>Photometry:</b>
        <PlotContainer url={`/plot_photometry/${id}`}/>

        <br/>
        <b>Spectroscopy:</b><br/>
        <PlotContainer url={`/plot_spectroscopy/${id}`}/>
    </div>
    )
  }
};


export default Source;
