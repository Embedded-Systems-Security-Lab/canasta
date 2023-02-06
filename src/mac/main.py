import argparse
from Can_MAC_example import generate_data
def main():
    
    parser = argparse.ArgumentParser(description="Bus speed and data-size")
    parser.add_argument("--data_size", type = int, required=True)
    parser.add_argument("--bus_speed",type = int,required=True)
    args = parser.parse_args()
    
    response_time = generate_data(args.bus_speed, args.data_size)
    print(response_time)
           
if __name__ == '__main__':
    main()        
         