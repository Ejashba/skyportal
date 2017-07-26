import React from 'react';
import styles from './CommentEntry.css';


class CommentEntry extends React.Component {
  constructor(props) {
    super(props);
//    {source, handleSubmit} = this.props;

    this.state = {value: ''};
    this._handleSubmit = this._handleSubmit.bind(this);
    this._handleChange = this._handleChange.bind(this);
  }

  _handleSubmit = (event) => {
    console.log('Submitted:', this.state.value);
    this.props.handleSubmit({text: this.state.value,
                             source: this.props.source});
    this.setState({value: ""});
    event.preventDefault();
  };

  _handleChange = (event) => {
    this.setState({value: event.target.value});
  }

  render() {
    return (
      <form className={styles.commentEntry} onSubmit={this._handleSubmit}>
        <label>
          <input type="text" name="comment" value={this.state.value}
                 onChange={this._handleChange}/>
        </label>
        <input type="submit" value="↵"/>
      </form>
    );
  }
};

export default CommentEntry;