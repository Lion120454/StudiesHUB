using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace ССП_1
{
        public class advComboBox : ComboBox
        {
            private List<string> _items = new List<string>();

            public advComboBox()//Конструктор
            {
                this.DropDownStyle = ComboBoxStyle.DropDown;
                this.TextChanged += AdvComboBox_TextChanged;
            }

            public void SetItems(List<string> items)// Установка оригинального списка
        {
                _items = new List<string>(items);
                this.Items.Clear();
                this.Items.AddRange(_items.ToArray());
            }

            
            private void AdvComboBox_TextChanged(object sender, EventArgs e)// Фильтрация при изменении текста
            {
                string text = this.Text;
                var filtered = _items.Where(x => x.IndexOf(text, StringComparison.OrdinalIgnoreCase) >= 0).ToList();

                this.BeginUpdate();
                this.Items.Clear();
                this.Items.AddRange(filtered.ToArray());
                this.DroppedDown = true;
                this.SelectionStart = this.Text.Length;
                this.SelectionLength = 0;
                this.EndUpdate();
            }
        }
}
