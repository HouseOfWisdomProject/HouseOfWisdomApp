import React from 'react';

{/*this is just test profiles to show Student Check in and Check Out*/}
const dummyStudents = [
  { id: 1, name: 'Abby White', grade: '4th Grade' },
  { id: 2, name: 'Leo Vasquez', grade: '5th Grade' },
  { id: 3, name: 'Sofia Jones', grade: '2nd Grade' },
  { id: 4, name: 'Evie Smith', grade: '9th Grade' },
];

const StudentAttendance = () => {
  return (
    <div style={styles.container}>
      <div style={styles.grid}>
        {dummyStudents.map(student => (
          <div key={student.id} style={styles.card}>
            <div>
              <strong>{student.name}</strong>
              <p>{student.grade}</p>
            </div>
            <div>
              <button style={styles.punchButton}>Check In</button>
              <button style={styles.punchButton}>Check Out</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '15px',
  },
  card: {
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '15px',
    backgroundColor: '#fafafa',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    justifyContent: 'space-between',
  },
  punchButton: {
    marginRight: '10px',
    padding: '8px 12px',
    backgroundColor: '#e97634ff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

export default StudentAttendance;
