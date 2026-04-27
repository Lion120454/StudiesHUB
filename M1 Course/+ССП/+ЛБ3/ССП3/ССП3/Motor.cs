using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ССП3
{
    public abstract class Motor
    {
        public float Frequency { get; protected set; }//Частота
        public bool IsRunning { get; protected set; }

        protected Motor()
        {
            Frequency = 0;
            IsRunning = false;
        }

        public abstract void SetFrequency(float frequency);
        public abstract void Start();
        public abstract void Stop();
        public abstract void Reverse();

        public virtual Dictionary<string, object> GetStatus()
        {
            return new Dictionary<string, object>
        {
            { "type", GetType().Name },
            { "current_frequency", Frequency },
            { "is_running", IsRunning }
        };
        }
    }
}
