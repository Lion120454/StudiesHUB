using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace ССП_1
{
    public partial class Form1 : Form
    {
        private advComboBox comboBox;
        public Form1()
        {
            InitializeComponent();

            comboBox = new advComboBox
            {
                Left = 20,
                Top = 20,
                Width = 200
            };
            this.Controls.Add(comboBox);

            
            List<string> items = new List<string>// Пример данных
            {
                "Apple", "Banana", "Orange", "Grapes", "Pineapple",
                "Mango", "Strawberry", "Blueberry", "Blackberry"
            };

            comboBox.SetItems(items);
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }
    }
}
