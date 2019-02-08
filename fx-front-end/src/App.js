import React, { Component } from 'react';
import fx_logo from './assets/fx-logo.png'
import './App.css';
import axios from 'axios';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import LinearProgress from '@material-ui/core/LinearProgress';
import AGD from './assets/AGD.png';
import AYA from './assets/AYA.png';
import CB from './assets/CB.png';
import KBZ from './assets/KBZ.png';
import MAB from './assets/MAB.png';
import UAB from './assets/UAB.png';
import Central_Bank from './assets/Central_Bank.png';
import JO from './assets/JO.png';
var moment = require('moment-timezone');

const bank_logo = {
  'AYA' : AYA,
  'AGD' : AGD,
  'CB'  : CB,
  'KBZ' : KBZ,
  'MAB' : MAB,
  'UAB' : UAB,
  'Central Bank' : Central_Bank
}

const bank_link = {
  'AYA' : 'https://www.ayabank.com/en_US/',
  'AGD' : 'https://agdbank.com/',
  'CB'  : 'https://www.cbbank.com.mm/',
  'KBZ' : 'https://www.kbzbank.com/en/',
  'MAB' : 'https://www.mabbank.com/',
  'UAB' : 'http://www.unitedamarabank.com/',
  'Central Bank' : 'https://forex.cbm.gov.mm/index.php/fxrate'
}

const styles = {
  footer: {
    padding: '0.5rem',
    fontSize: '1rem',
    backgroundColor: '#1f1f1f',
    textAlign: 'center',
    color: 'white',
    width: '100%',
    bottom: 0
  },
  table: {
    minWidth: 300
  }
}


const API_URL="https://us-central1-shwecity-203616.cloudfunctions.net/fx-api";
const TOKEN=""

class App extends Component {
  state = {
    currency: 'USD',
    rates: [],
    best_sell: {},
    best_buy: {},
    updated_at: "",
    loading: true
  };

  componentDidMount() {
    axios.get(API_URL + '?currency=USD' + "&api-token=" + TOKEN)
    .then(res => {
      let utc = moment.tz(res.data.updated_at, 'Europe/London');
      let updated_at = utc.clone().tz(moment.tz.guess());
      this.setState({
        rates: res.data.rates,
        best_sell: res.data.SELL,
        best_buy: res.data.BUY,
        updated_at: updated_at.format('DD-MM-YYYY HH:mm'),
        loading: false
      });
    })
  }

  handleChange = event => {
    this.setState({
      loading: true
    });

    let currency = event.target.value
    axios.get(API_URL + '?currency=' + currency + "&api-token=" + TOKEN)
    .then(res=> {
      let utc = moment.tz(res.data.updated_at, 'Europe/London');
      let updated_at = utc.clone().tz(moment.tz.guess());
      this.setState({
        rates: res.data.rates,
        currency: currency,
        best_sell: res.data.SELL,
        best_buy: res.data.BUY,
        updated_at: updated_at.format('DD-MM-YYYY HH:mm'),
        loading: false
      });
    })
  };
  
  render() {

    const buy_col = this.state.currency + '_BUY';
    const sell_col = this.state.currency + '_SELL';
    return (
      <div className="App">
        {this.state.loading &&
          <LinearProgress />  
        }
        <div className="App-container"> 
          <header className="App-header">
            <img src={fx_logo} className="App-logo" alt="logo" />
          </header>
          <div className="row currency-container">
            <p className="currency-label">Currency:</p>
              <Select
                className="currency-dropdown"
                value={this.state.currency}
                onChange={this.handleChange}
              >
                <MenuItem value='USD'>USD</MenuItem>
                <MenuItem value='EUR'>EUR</MenuItem>
                <MenuItem value='SGD'>SGD</MenuItem>
                <MenuItem value='MYR'>MYR</MenuItem>
                <MenuItem value='THB'>THB</MenuItem>
              </Select>
          </div>
          <div className="table-container">
              <Table style={{ width: 300, tableLayout: 'auto' }} fixedHeader={false}>
                <TableHead>
                  <TableRow>
                    <TableCell><b>Bank</b></TableCell>
                    <TableCell style={{width: "40"}}>Bank Buy</TableCell>
                    <TableCell>Bank Sell</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {
                    this.state.rates.map((rate) => 
                      <TableRow key={rate.bank}>
                        <TableCell align="left" style={{ padding: "0px" }}><a href={bank_link[rate.bank]} target="_blank"><img src={bank_logo[rate.bank]} alt="bank-logo.png" width="50"></img></a></TableCell>  
                        <TableCell align="center" style={{ padding: "0px" }} className={(rate.bank == this.state.best_buy.bank) ? 'table-cell' : ''}>{rate[buy_col]}</TableCell>
                        <TableCell align="center" style={{ padding: "0px" }} className={(rate.bank == this.state.best_sell.bank) ? 'table-cell' : ''}>{rate[sell_col]}</TableCell>
                      </TableRow>
                    )

                  }
                </TableBody>
              </Table>
            </div>
            <div className="row last-update-container">
              <p className="last-update-label">Last Updated At: </p>
              <p className="last-update-label">{this.state.updated_at}</p>
            </div>
            <div className="row disclaimer-container">
                <p className="disclaimer"><i><b>**Disclaimer**</b>: This website is a public resource of information which is intended, but not promised or guaranteed, to be correct, complete and up-to-date. 
                Any action you take upon the information on this website is strictly at your own risk. You assume full responsibility for the risk or loss resulting from your use of this site and your reliance on the material and information contained on it.</i></p>
            </div>
          </div>
          <footer style={styles.footer}>
              Build with ♥ by <a href="https://www.facebook.com/Jo-The-Cloud-Ninja-537752086741170" target="_blank">Jo - The Cloud Ninja <img src={JO} width="30" alt="jo_logo" /></a>
          </footer>
      </div>
    );
  }
}

export default App;
