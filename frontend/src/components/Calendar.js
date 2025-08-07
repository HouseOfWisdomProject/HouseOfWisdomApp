import React from 'react';

const Calendar = () => {
  return (
    <div style={styles.calendarContainer}>
      <iframe
        src="https://calendar.google.com/calendar/embed?src=your_calendar_id%40group.calendar.google.com&ctz=America%2FLos_Angeles"
        style={styles.iframe}
        frameBorder="0"
        scrolling="no"
        title="Shared Google Calendar"
      ></iframe>
    </div>
  );
};

const styles = {
  calendarContainer: {
    width: '100%',
    height: '700px',
    backgroundColor: '#f9f9f9',
    borderRadius: '10px',
    overflow: 'hidden',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
  },
  iframe: {
    width: '100%',
    height: '100%',
    border: '0',
  },
};

export default Calendar;
